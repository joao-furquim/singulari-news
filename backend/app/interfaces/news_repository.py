"""Interface for news article repository.

Defines the persistence contract for retrieving, creating, updating, and
deleting news articles. All concrete repositories must implement this
interface so that services remain decoupled from the ORM layer.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from app.models.news import News
from app.schemas.news import NewsFilter


class INewsRepository(ABC):
    """Abstract base class defining the news article persistence contract."""

    @abstractmethod
    async def find_all(
        self, news_filter: NewsFilter, favorited_ids: set[UUID]
    ) -> tuple[list[News], int]:
        """Retrieve a paginated list of news articles matching the given filters.

        :param news_filter: Filter parameters including date range, category slugs,
                            page number, and items per page.
        :param favorited_ids: Set of news UUIDs the current user has favorited;
                              used to annotate each result with ``is_favorited``.
        :return: A tuple of ``(news_items, total_count)`` where ``news_items`` is
                 the current page slice and ``total_count`` is the total matching rows.
        """

    @abstractmethod
    async def find_by_id(self, news_id: UUID) -> News | None:
        """Retrieve a single news article by its UUID.

        :param news_id: UUID of the article to look up.
        :return: The ``News`` instance with its related category pre-fetched,
                 or ``None`` if no article with that ID exists.
        """

    @abstractmethod
    async def create(self, news_data: dict) -> News:
        """Persist a new news article.

        :param news_data: Dictionary of field values for the new record.
        :return: The newly created ``News`` instance.
        """

    @abstractmethod
    async def update(self, news_id: UUID, news_data: dict) -> News:
        """Apply a partial update to an existing news article.

        :param news_id: UUID of the article to update.
        :param news_data: Dictionary of fields to patch; only provided keys are written.
        :return: The updated ``News`` instance with its related category pre-fetched.
        """

    @abstractmethod
    async def delete(self, news_id: UUID) -> None:
        """Delete a news article by its UUID.

        :param news_id: UUID of the article to delete.
        """
