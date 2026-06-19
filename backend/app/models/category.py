"""Tortoise ORM model for news categories.

Categories are seeded at application startup and used to classify articles.
The ``slug`` field is the canonical identifier used in API filter parameters
and user preference slugs.
"""

from tortoise import fields
from tortoise.models import Model


class Category(Model):
    """A news category stored in the ``categories`` table.

    Categories are created once via the startup seed and are not user-editable.
    The ``slug`` (e.g. ``"technology"``) is used as the primary identifier in
    filter queries and preference responses.
    """

    id = fields.UUIDField(primary_key=True)
    name = fields.CharField(max_length=100, unique=True)
    slug = fields.CharField(max_length=100, unique=True)
    icon = fields.CharField(max_length=50, null=True)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "categories"
