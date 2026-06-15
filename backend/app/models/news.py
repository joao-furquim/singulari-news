from tortoise import fields
from tortoise.models import Model


class News(Model):
    id = fields.UUIDField(pk=True)
    category = fields.ForeignKeyField("models.Category", related_name="news_items")
    title = fields.CharField(max_length=500)
    source = fields.CharField(max_length=255)
    summary = fields.TextField(null=True)
    content = fields.TextField()
    published_at = fields.DatetimeField()
    ai_generated = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "news"


class NewsQueue(Model):
    id = fields.UUIDField(pk=True)
    news = fields.ForeignKeyField("models.News", related_name="queue_entries")
    status = fields.CharField(max_length=50, default="pending")
    error_message = fields.TextField(null=True)
    processed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "news_queue"
