"""Concrete user repository using Tortoise ORM.

Implements ``IUserRepository`` against the ``users``, ``user_preferences``,
``user_favorites``, and ``password_resets`` tables.
"""

from uuid import UUID

from app.interfaces.user_repository import IUserRepository
from app.models.user import PasswordReset, User, UserFavorite, UserPreference, UserRole


class UserRepository(IUserRepository):
    """Tortoise ORM implementation of the user persistence layer."""

    async def find_by_id(self, user_id: UUID) -> User | None:
        """Look up a user by their UUID.

        :param user_id: UUID of the user to retrieve.
        :return: The ``User`` instance, or ``None`` if not found.
        """
        return await User.get_or_none(id=user_id)

    async def find_by_email(self, email: str) -> User | None:
        """Look up a user by their email address.

        :param email: Email address to search for (case-sensitive).
        :return: The ``User`` instance, or ``None`` if not found.
        """
        return await User.get_or_none(email=email)

    async def find_all(self) -> list[User]:
        """Retrieve all non-root users.

        :return: List of all ``User`` instances excluding the root account.
        """
        return await User.filter(role__not=UserRole.root)

    async def find_all_paginated(self, page: int, limit: int) -> tuple[list[User], int]:
        """Retrieve a paginated list of non-root users ordered by creation date.

        :param page: 1-based page number.
        :param limit: Maximum number of users per page.
        :return: Tuple of ``(users, total_count)`` for the requested page.
        """
        query = User.filter(role__not=UserRole.root).order_by("created_at")
        total = await query.count()
        offset = (page - 1) * limit
        users = await query.offset(offset).limit(limit)
        return list(users), total

    async def create(self, user_data: dict) -> User:
        """Persist a new user record.

        :param user_data: Dictionary of field values for the new user.
        :return: The newly created ``User`` instance.
        """
        return await User.create(**user_data)

    async def update(self, user_id: UUID, user_data: dict) -> User:
        """Apply a partial update to a user record and return the refreshed record.

        :param user_id: UUID of the user to update.
        :param user_data: Fields to patch; only provided keys are written.
        :return: The updated ``User`` instance.
        """
        await User.filter(id=user_id).update(**user_data)
        return await User.get(id=user_id)

    async def delete(self, user_id: UUID) -> None:
        """Delete a user record.

        :param user_id: UUID of the user to delete.
        """
        await User.filter(id=user_id).delete()

    async def get_preference_ids(self, user_id: UUID) -> list[UUID]:
        """Retrieve the category UUIDs saved as the user's preferences.

        :param user_id: UUID of the user.
        :return: List of category UUIDs.
        """
        preferences = await UserPreference.filter(user_id=user_id).values_list(
            "category_id", flat=True
        )
        return list(preferences)

    async def get_preference_slugs(self, user_id: UUID) -> list[str]:
        """Retrieve the category slugs saved as the user's preferences.

        Performs a single query with ``prefetch_related`` to resolve slugs
        from the related ``Category`` model.

        :param user_id: UUID of the user.
        :return: List of category slug strings (e.g. ``["technology", "ai"]``).
        """
        prefs = await UserPreference.filter(user_id=user_id).prefetch_related(
            "category"
        )
        return [pref.category.slug for pref in prefs]

    async def set_preferences(self, user_id: UUID, category_ids: list[UUID]) -> None:
        """Replace the user's category preferences with a new set.

        Atomically deletes all existing preferences before bulk-inserting
        the new ones.

        :param user_id: UUID of the user.
        :param category_ids: List of category UUIDs to set as preferences.
        """
        await UserPreference.filter(user_id=user_id).delete()
        preference_objects = [
            UserPreference(user_id=user_id, category_id=category_id)
            for category_id in category_ids
        ]
        await UserPreference.bulk_create(preference_objects)

    async def get_favorite_news_ids(self, user_id: UUID) -> set[UUID]:
        """Retrieve the set of news UUIDs the user has favorited.

        :param user_id: UUID of the user.
        :return: Set of favorited news UUIDs.
        """
        favorite_ids = await UserFavorite.filter(user_id=user_id).values_list(
            "news_id", flat=True
        )
        return set(favorite_ids)

    async def save_password_reset(self, reset_data: dict) -> PasswordReset:
        """Persist a new password-reset token record.

        :param reset_data: Dictionary containing ``user_id``, ``token``,
                           and ``expires_at``.
        :return: The newly created ``PasswordReset`` instance.
        """
        return await PasswordReset.create(**reset_data)

    async def find_valid_reset_token(self, token: str) -> PasswordReset | None:
        """Look up an active, unexpired password-reset record by token string.

        :param token: The raw reset token to search for.
        :return: A valid ``PasswordReset`` instance, or ``None`` if the token
                 is missing, already used, or past its expiry.
        """
        from datetime import datetime, timezone

        return await PasswordReset.get_or_none(
            token=token,
            is_used=False,
            expires_at__gt=datetime.now(timezone.utc),
        )
