"""Tortoise ORM models for news articles and the processing queue.

``News`` represents a curated article ingested by the agent pipeline.
``NewsQueue`` tracks the processing status of each article as it moves
through the consumer worker.
"""

from tortoise import fields
from tortoise.models import Model


class News(Model):
    """A curated news article stored in the ``news`` table.

    Articles are created by the NestJS consumer after the AI pipeline
    generates a summary. The ``category`` foreign key links each article
    to one of the predefined ``Category`` records.
    """

    id = fields.UUIDField(primary_key=True)
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
    """Processing queue entry for a news article in the ``news_queue`` table.

    Tracks whether the consumer worker has successfully processed an article,
    and stores any error message when processing fails.
    """

    id = fields.UUIDField(primary_key=True)
    news = fields.ForeignKeyField("models.News", related_name="queue_entries")
    status = fields.CharField(max_length=50, default="pending")
    error_message = fields.TextField(null=True)
    processed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "news_queue"
