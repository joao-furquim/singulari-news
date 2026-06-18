from enum import Enum

from tortoise import fields
from tortoise.models import Model


class UserRole(str, Enum):
    user = "user"
    reviewer = "reviewer"
    admin = "admin"
    root = "root"


class User(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)
    avatar_url = fields.CharField(max_length=500, null=True)
    locale = fields.CharField(max_length=10, default="pt-BR")
    role = fields.CharEnumField(UserRole, default=UserRole.user, max_length=20)
    must_change_password = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"


class UserPreference(Model):
    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="user_preferences")
    category = fields.ForeignKeyField(
        "models.Category", related_name="user_preferences"
    )
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_preferences"
        unique_together = (("user", "category"),)


class UserFavorite(Model):
    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="user_favorites")
    news = fields.ForeignKeyField("models.News", related_name="user_favorites")
    saved_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_favorites"
        unique_together = (("user", "news"),)


class PasswordReset(Model):
    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="password_resets")
    token = fields.CharField(max_length=500, unique=True)
    is_used = fields.BooleanField(default=False)
    expires_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "password_resets"
