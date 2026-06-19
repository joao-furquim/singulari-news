"""Tortoise ORM models for users and related entities.

Defines the ``User`` account model, ``UserPreference`` (category subscriptions),
``UserFavorite`` (saved articles), ``PasswordReset`` (one-time reset tokens),
and the ``UserRole`` enumeration.
"""

from enum import Enum

from tortoise import fields
from tortoise.models import Model


class UserRole(str, Enum):
    """Enumeration of possible user roles in ascending privilege order.

    - ``user`` — standard reader account.
    - ``reviewer`` — can edit and delete news articles.
    - ``admin`` — can manage users (invite, change roles, delete).
    - ``root`` — superuser created at startup; cannot be deleted or modified.
    """

    user = "user"
    reviewer = "reviewer"
    admin = "admin"
    root = "root"


class User(Model):
    """A registered user account stored in the ``users`` table."""

    id = fields.UUIDField(primary_key=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)
    locale = fields.CharField(max_length=10, default="pt-BR")
    role = fields.CharEnumField(UserRole, default=UserRole.user, max_length=20)
    must_change_password = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"


class UserPreference(Model):
    """A user's category subscription stored in the ``user_preferences`` table.

    Each row represents a single (user, category) pair. Deleting all rows
    for a user and bulk-inserting new ones is the preferred update strategy.
    """

    id = fields.UUIDField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="user_preferences")
    category = fields.ForeignKeyField(
        "models.Category", related_name="user_preferences"
    )
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_preferences"
        unique_together = (("user", "category"),)


class UserFavorite(Model):
    """A news article saved by a user, stored in the ``user_favorites`` table."""

    id = fields.UUIDField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="user_favorites")
    news = fields.ForeignKeyField("models.News", related_name="user_favorites")
    saved_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_favorites"
        unique_together = (("user", "news"),)


class PasswordReset(Model):
    """A one-time password-reset token stored in the ``password_resets`` table.

    Tokens expire after ``JWT_RESET_TOKEN_EXPIRE_MINUTES`` and are marked
    ``is_used=True`` once the password is successfully changed.
    """

    id = fields.UUIDField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="password_resets")
    token = fields.CharField(max_length=500, unique=True)
    is_used = fields.BooleanField(default=False)
    expires_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "password_resets"
