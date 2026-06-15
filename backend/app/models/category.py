from tortoise import fields
from tortoise.models import Model


class Category(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    slug = fields.CharField(max_length=100, unique=True)
    icon = fields.CharField(max_length=50, null=True)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "categories"
