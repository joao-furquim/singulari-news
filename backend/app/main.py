from contextlib import asynccontextmanager

from app.api.routes import auth, news, preferences, users
from app.core.config import TORTOISE_ORM
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import RegisterTortoise


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with RegisterTortoise(app, config=TORTOISE_ORM):
        await _seed_categories()
        await _seed_admin()
        yield


async def _seed_categories():
    from app.models.category import Category

    seed_categories = [
        {"name": "Technology", "slug": "technology", "icon": "💻"},
        {"name": "AI", "slug": "ai", "icon": "🤖"},
        {"name": "Business", "slug": "business", "icon": "💼"},
        {"name": "Science", "slug": "science", "icon": "🔬"},
        {"name": "Health", "slug": "health", "icon": "🏥"},
        {"name": "Politics", "slug": "politics", "icon": "🏛️"},
        {"name": "Sports", "slug": "sports", "icon": "🏆"},
        {"name": "General", "slug": "general", "icon": "📰"},
    ]
    for category_data in seed_categories:
        await Category.get_or_create(slug=category_data["slug"], defaults=category_data)


async def _seed_admin():
    from app.core.security import hash_password
    from app.models.user import User, UserRole

    await User.get_or_create(
        email="root@singulari.com",
        defaults={
            "name": "Root Singulari",
            "password_hash": hash_password("Root@123"),
            "role": UserRole.root,
            "must_change_password": False,
        },
    )
    await User.get_or_create(
        email="admin@singulari.com",
        defaults={
            "name": "Admin Singulari",
            "password_hash": hash_password("Admin@123"),
            "role": UserRole.admin,
            "must_change_password": False,
        },
    )


app = FastAPI(title="Singulari News API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(news.router)
app.include_router(users.router)
app.include_router(preferences.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
