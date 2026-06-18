"""
Demo seed — creates sample users for development and demonstration.

Usage (via docker-compose):
  docker compose --profile demo up seed-demo

Direct usage (inside backend container):
  python -m app.core.seed_demo
"""

import asyncio

from tortoise import Tortoise

from app.core.config import TORTOISE_ORM
from app.core.security import hash_password
from app.models.user import User, UserRole

DEMO_USERS = [
    {
        "email": "reviewer@singulari.com",
        "name": "Reviewer Singulari",
        "password": "Reviewer@123",
        "role": UserRole.reviewer,
    },
    {
        "email": "editor@singulari.com",
        "name": "Editor Singulari",
        "password": "Editor@123",
        "role": UserRole.reviewer,
    },
    {
        "email": "user1@singulari.com",
        "name": "User One",
        "password": "User@123",
        "role": UserRole.user,
    },
    {
        "email": "user2@singulari.com",
        "name": "User Two",
        "password": "User@123",
        "role": UserRole.user,
    },
]


async def main() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    print("Connected to database")

    for entry in DEMO_USERS:
        _, created = await User.get_or_create(
            email=entry["email"],
            defaults={
                "name": entry["name"],
                "password_hash": hash_password(entry["password"]),
                "role": entry["role"],
                "must_change_password": False,
            },
        )
        status = "created" if created else "already exists"
        print(f"  [{status}] {entry['email']} (role: {entry['role'].value})")

    await Tortoise.close_connections()
    print("Demo seed complete.")


if __name__ == "__main__":
    asyncio.run(main())
