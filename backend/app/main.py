from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import RegisterTortoise

from app.api.routes import auth, news, preferences, users
from app.core.config import TORTOISE_ORM


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with RegisterTortoise(app, config=TORTOISE_ORM):
        await _seed_categories()
        await _seed_admin()
        yield


async def _seed_categories():
    from app.models.category import Category

    seed_categories = [
        {"name": "Tecnologia", "slug": "tecnologia", "icon": "💻"},
        {"name": "IA", "slug": "ia", "icon": "🤖"},
        {"name": "Negócios", "slug": "negocios", "icon": "💼"},
        {"name": "Inovação", "slug": "inovacao", "icon": "🚀"},
        {"name": "Ciência", "slug": "ciencia", "icon": "🔬"},
        {"name": "Política", "slug": "politica", "icon": "🏛️"},
    ]
    for category_data in seed_categories:
        await Category.get_or_create(slug=category_data["slug"], defaults=category_data)


async def _seed_admin():
    from app.core.security import hash_password
    from app.models.user import User, UserRole

    await User.get_or_create(
        email="admin@singulari.com",
        defaults={
            "name": "Admin Singulari",
            "password_hash": hash_password("Admin@123"),
            "role": UserRole.admin,
        },
    )


app = FastAPI(title="Singulari News API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
