"""Shared pytest fixtures for all backend unit tests."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from app.schemas.news import CategoryOut, NewsOut
from app.schemas.user import UserOut

# ── Stable IDs so assertions can reference them ──────────────────────────────

USER_ID: UUID = uuid4()
ADMIN_ID: UUID = uuid4()
ROOT_ID: UUID = uuid4()
NEWS_ID: UUID = uuid4()
CAT_ID: UUID = uuid4()


# ── User fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture
def sample_user() -> UserOut:
    return UserOut(
        id=USER_ID,
        name="Regular User",
        email="user@test.com",
        locale="en",
        role="user",
        must_change_password=False,
        created_at=datetime(2026, 1, 1),
    )


@pytest.fixture
def sample_admin() -> UserOut:
    return UserOut(
        id=ADMIN_ID,
        name="Admin User",
        email="admin@test.com",
        locale="en",
        role="admin",
        must_change_password=False,
        created_at=datetime(2026, 1, 1),
    )


@pytest.fixture
def sample_root() -> UserOut:
    return UserOut(
        id=ROOT_ID,
        name="Root User",
        email="root@test.com",
        locale="en",
        role="root",
        must_change_password=False,
        created_at=datetime(2026, 1, 1),
    )


# ── Repository mocks ─────────────────────────────────────────────────────────


@pytest.fixture
def mock_user_repository() -> MagicMock:
    repo = MagicMock()
    repo.find_by_email = AsyncMock(return_value=None)
    repo.find_by_id = AsyncMock(return_value=None)
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.find_all = AsyncMock(return_value=[])
    repo.find_all_paginated = AsyncMock(return_value=([], 0))
    repo.get_preference_ids = AsyncMock(return_value=[])
    repo.get_favorite_news_ids = AsyncMock(return_value=set())
    return repo


@pytest.fixture
def mock_news_repository() -> MagicMock:
    repo = MagicMock()
    repo.find_all = AsyncMock(return_value=([], 0))
    repo.find_by_id = AsyncMock(return_value=None)
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


# ── Service dependency mocks ──────────────────────────────────────────────────


@pytest.fixture
def mock_email_service() -> MagicMock:
    svc = MagicMock()
    svc.send_password_reset = AsyncMock()
    return svc


# ── News data helpers ─────────────────────────────────────────────────────────


@pytest.fixture
def sample_category_out() -> CategoryOut:
    return CategoryOut(
        id=CAT_ID,
        name="Technology",
        slug="technology",
        icon="💻",
        description=None,
    )


@pytest.fixture
def sample_news_out(sample_category_out: CategoryOut) -> NewsOut:
    return NewsOut(
        id=NEWS_ID,
        category=sample_category_out,
        title="Test Article Title",
        source="Test Source",
        summary="A concise AI-generated summary.",
        content="Full article content goes here.",
        published_at=datetime(2026, 6, 18, 10, 0, 0),
        ai_generated=True,
        created_at=datetime(2026, 6, 18, 10, 0, 0),
        is_favorited=False,
    )


def make_db_user_mock(
    *,
    user_id: UUID | None = None,
    name: str = "Test User",
    email: str = "test@test.com",
    role: str = "user",
    password_hash: str = "hashed_pw",
) -> MagicMock:
    """Create a MagicMock that behaves like a Tortoise User model instance.

    Sets all attributes that UserOut.model_validate(from_attributes=True) reads.
    """
    user = MagicMock()
    user.id = user_id or uuid4()
    user.name = name
    user.email = email
    user.locale = "en"
    user.role = role
    user.must_change_password = False
    user.created_at = datetime(2026, 1, 1)
    user.password_hash = password_hash
    return user
