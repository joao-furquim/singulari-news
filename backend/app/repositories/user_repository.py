from uuid import UUID

from app.interfaces.user_repository import IUserRepository
from app.models.user import PasswordReset, User, UserFavorite, UserPreference


class UserRepository(IUserRepository):
    async def find_by_id(self, user_id: UUID) -> User | None:
        return await User.get_or_none(id=user_id)

    async def find_by_email(self, email: str) -> User | None:
        return await User.get_or_none(email=email)

    async def find_all(self) -> list[User]:
        return await User.all()

    async def create(self, user_data: dict) -> User:
        return await User.create(**user_data)

    async def update(self, user_id: UUID, user_data: dict) -> User:
        await User.filter(id=user_id).update(**user_data)
        return await User.get(id=user_id)

    async def delete(self, user_id: UUID) -> None:
        await User.filter(id=user_id).delete()

    async def get_preference_ids(self, user_id: UUID) -> list[UUID]:
        preferences = await UserPreference.filter(user_id=user_id).values_list(
            "category_id", flat=True
        )
        return list(preferences)

    async def set_preferences(self, user_id: UUID, category_ids: list[UUID]) -> None:
        await UserPreference.filter(user_id=user_id).delete()
        preference_objects = [
            UserPreference(user_id=user_id, category_id=category_id)
            for category_id in category_ids
        ]
        await UserPreference.bulk_create(preference_objects)

    async def get_favorite_news_ids(self, user_id: UUID) -> set[UUID]:
        favorite_ids = await UserFavorite.filter(user_id=user_id).values_list(
            "news_id", flat=True
        )
        return set(favorite_ids)

    async def save_password_reset(self, reset_data: dict) -> PasswordReset:
        return await PasswordReset.create(**reset_data)

    async def find_valid_reset_token(self, token: str):
        from datetime import datetime, timezone

        return await PasswordReset.get_or_none(
            token=token,
            is_used=False,
            expires_at__gt=datetime.now(timezone.utc),
        )
