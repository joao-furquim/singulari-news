"""Shared fixtures for integration tests.

Uses SQLite in-memory so tests run without a real PostgreSQL server.
Tortoise ORM is initialized fresh for each test function.
"""

from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from tortoise import Tortoise

from app.api.routes import auth, news, preferences, users
from app.core.security import create_access_token, hash_password
from app.models.user import User, UserRole

# ── SQLite test models (no aerich tracking table needed) ─────────────────────

TEST_MODULES = {
    "models": [
        "app.models.user",
        "app.models.category",
        "app.models.news",
    ]
}


@asynccontextmanager
async def _noop_lifespan(app: FastAPI):
    yield


def _make_test_app() -> FastAPI:
    """FastAPI app without the production lifespan (no PostgreSQL registration)."""
    app = FastAPI(lifespan=_noop_lifespan)
    app.include_router(auth.router)
    app.include_router(news.router)
    app.include_router(users.router)
    app.include_router(preferences.router)
    return app


TEST_APP = _make_test_app()


# ── Per-test database ─────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
async def db():
    """Initialize a fresh SQLite in-memory DB for every test."""
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules=TEST_MODULES,
    )
    await Tortoise.generate_schemas(safe=True)

    # Seed categories and admin/root users (mirrors production main.py)
    from app.models.category import Category

    for data in [
        {"name": "Technology", "slug": "technology", "icon": "💻"},
        {"name": "AI", "slug": "ai", "icon": "🤖"},
        {"name": "Business", "slug": "business", "icon": "💼"},
        {"name": "Science", "slug": "science", "icon": "🔬"},
        {"name": "Health", "slug": "health", "icon": "🏥"},
        {"name": "Politics", "slug": "politics", "icon": "🏛️"},
        {"name": "Sports", "slug": "sports", "icon": "🏆"},
        {"name": "General", "slug": "general", "icon": "📰"},
    ]:
        await Category.get_or_create(slug=data["slug"], defaults=data)

    await User.get_or_create(
        email="root@singulari.com",
        defaults={
            "name": "Root",
            "password_hash": hash_password("Root@123"),
            "role": UserRole.root,
            "must_change_password": False,
        },
    )
    await User.get_or_create(
        email="admin@singulari.com",
        defaults={
            "name": "Admin",
            "password_hash": hash_password("Admin@123"),
            "role": UserRole.admin,
            "must_change_password": False,
        },
    )

    yield

    await Tortoise.close_connections()


# ── HTTP client ───────────────────────────────────────────────────────────────


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=TEST_APP),
        base_url="http://test",
    ) as ac:
        yield ac


# ── JWT token fixtures ────────────────────────────────────────────────────────


@pytest.fixture
async def admin_token() -> str:
    admin = await User.get(email="admin@singulari.com")
    return create_access_token(str(admin.id))


@pytest.fixture
async def user_token() -> str:
    user, _ = await User.get_or_create(
        email="regularuser@test.com",
        defaults={
            "name": "Regular User",
            "password_hash": hash_password("User@123"),
            "role": UserRole.user,
            "must_change_password": False,
        },
    )
    return create_access_token(str(user.id))
