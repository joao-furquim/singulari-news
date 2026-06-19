"""Interface for user repository.

Defines the persistence contract for user accounts, category preferences,
news favorites, and password-reset tokens. Concrete implementations must
fulfil this contract; services depend solely on this interface.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from app.models.user import PasswordReset, User


class IUserRepository(ABC):
    """Abstract base class defining the user persistence contract."""

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> User | None:
        """Look up a user by their UUID.

        :param user_id: UUID of the user to retrieve.
        :return: The ``User`` instance, or ``None`` if not found.
        """

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        """Look up a user by their email address.

        :param email: Email address to search for (case-sensitive).
        :return: The ``User`` instance, or ``None`` if not found.
        """

    @abstractmethod
    async def find_all(self) -> list[User]:
        """Retrieve all non-root users.

        :return: List of all ``User`` instances excluding the root account.
        """

    @abstractmethod
    async def find_all_paginated(self, page: int, limit: int) -> tuple[list[User], int]:
        """Retrieve a paginated list of non-root users ordered by creation date.

        :param page: 1-based page number.
        :param limit: Maximum number of users per page.
        :return: A tuple of ``(users, total_count)`` for the requested page.
        """

    @abstractmethod
    async def create(self, user_data: dict) -> User:
        """Persist a new user record.

        :param user_data: Dictionary of field values for the new user.
        :return: The newly created ``User`` instance.
        """

    @abstractmethod
    async def update(self, user_id: UUID, user_data: dict) -> User:
        """Apply a partial update to a user record.

        :param user_id: UUID of the user to update.
        :param user_data: Dictionary of fields to patch; only provided keys are written.
        :return: The updated ``User`` instance.
        """

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """Delete a user record.

        :param user_id: UUID of the user to delete.
        """

    @abstractmethod
    async def get_preference_ids(self, user_id: UUID) -> list[UUID]:
        """Retrieve the category UUIDs the user has selected as preferences.

        :param user_id: UUID of the user.
        :return: List of category UUIDs.
        """

    @abstractmethod
    async def get_preference_slugs(self, user_id: UUID) -> list[str]:
        """Retrieve the category slugs the user has selected as preferences.

        Preferred over ``get_preference_ids`` for API responses consumed by
        the frontend, which identifies categories by slug throughout.

        :param user_id: UUID of the user.
        :return: List of category slug strings (e.g. ``["technology", "ai"]``).
        """

    @abstractmethod
    async def set_preferences(self, user_id: UUID, category_ids: list[UUID]) -> None:
        """Replace the user's category preferences with a new set.

        Deletes all existing preferences before inserting the new ones.

        :param user_id: UUID of the user.
        :param category_ids: List of category UUIDs to set as preferences.
        """

    @abstractmethod
    async def get_favorite_news_ids(self, user_id: UUID) -> set[UUID]:
        """Retrieve the set of news UUIDs the user has favorited.

        :param user_id: UUID of the user.
        :return: Set of favorited news UUIDs.
        """

    @abstractmethod
    async def save_password_reset(self, reset_data: dict) -> PasswordReset:
        """Persist a password-reset token record.

        :param reset_data: Dictionary containing ``user_id``, ``token``,
                           and ``expires_at``.
        :return: The newly created ``PasswordReset`` instance.
        """

    @abstractmethod
    async def find_valid_reset_token(self, token: str) -> PasswordReset | None:
        """Look up an active, unexpired password-reset record by token string.

        :param token: The raw reset token to search for.
        :return: A valid ``PasswordReset`` instance, or ``None`` if the token
                 is missing, already used, or expired.
        """
