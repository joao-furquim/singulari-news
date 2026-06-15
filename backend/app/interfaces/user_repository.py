from abc import ABC, abstractmethod
from uuid import UUID

from app.models.user import PasswordReset, User


class IUserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> User | None:
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def find_all(self) -> list[User]:
        pass

    @abstractmethod
    async def create(self, user_data: dict) -> User:
        pass

    @abstractmethod
    async def update(self, user_id: UUID, user_data: dict) -> User:
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_preference_ids(self, user_id: UUID) -> list[UUID]:
        pass

    @abstractmethod
    async def set_preferences(self, user_id: UUID, category_ids: list[UUID]) -> None:
        pass

    @abstractmethod
    async def get_favorite_news_ids(self, user_id: UUID) -> set[UUID]:
        pass

    @abstractmethod
    async def save_password_reset(self, reset_data: dict) -> PasswordReset:
        pass

    @abstractmethod
    async def find_valid_reset_token(self, token: str) -> PasswordReset | None:
        pass
