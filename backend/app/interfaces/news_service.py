"""Interface for news article service.

Defines the business-logic contract for news operations including listing,
updating, deleting, and managing user favorites. Services that depend on
news functionality should program against this interface rather than a
concrete implementation.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from app.schemas.news import NewsFilter, NewsOut, NewsUpdateIn, PaginatedResponse


class INewsService(ABC):
    """Abstract base class defining the news business-logic contract."""

    @abstractmethod
    async def list_news(
        self, news_filter: NewsFilter, current_user_id: UUID | None
    ) -> PaginatedResponse:
        """Retrieve a paginated feed of news articles with optional filters.

        When ``current_user_id`` is provided, each article in the response is
        annotated with ``is_favorited`` based on the user's saved favorites.

        :param news_filter: Filter and pagination parameters (date range, categories,
                            page, limit).
        :param current_user_id: UUID of the authenticated user, or ``None`` for
                                anonymous requests.
        :return: A ``PaginatedResponse`` containing the current page of articles
                 plus pagination metadata.
        """

    @abstractmethod
    async def update_news(self, news_id: UUID, data: NewsUpdateIn) -> NewsOut:
        """Apply a partial update to a news article.

        :param news_id: UUID of the article to update.
        :param data: Fields to patch; ``None`` values are ignored.
        :return: The updated article serialised as ``NewsOut``.
        :raises HTTPException 404: When no article with ``news_id`` exists.
        """

    @abstractmethod
    async def delete_news(self, news_id: UUID) -> None:
        """Permanently delete a news article.

        :param news_id: UUID of the article to delete.
        :raises HTTPException 404: When no article with ``news_id`` exists.
        """

    @abstractmethod
    async def add_favorite(self, news_id: UUID, user_id: UUID) -> None:
        """Save a news article to a user's favorites.

        :param news_id: UUID of the article to favorite.
        :param user_id: UUID of the user who is favoriting.
        :raises HTTPException 404: When no article with ``news_id`` exists.
        :raises HTTPException 409: When the article is already in the user's favorites.
        """

    @abstractmethod
    async def remove_favorite(self, news_id: UUID, user_id: UUID) -> None:
        """Remove a news article from a user's favorites.

        :param news_id: UUID of the article to unfavorite.
        :param user_id: UUID of the user who is unfavoriting.
        :raises HTTPException 404: When the favorite record does not exist.
        """

    @abstractmethod
    async def list_favorites(self, user_id: UUID) -> list:
        """Retrieve all news articles saved as favorites by the given user.

        :param user_id: UUID of the user whose favorites to retrieve.
        :return: List of ``NewsOut`` items, each annotated with ``is_favorited=True``.
        """
