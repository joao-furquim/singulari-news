"""News service implementing business logic for article management.

Orchestrates news retrieval, pagination, favorite management, and article
mutations. Delegates all persistence to ``INewsRepository`` and, for
favorite look-ups, to ``UserRepository`` directly.
"""

from uuid import UUID

from app.interfaces.news_repository import INewsRepository
from app.interfaces.news_service import INewsService
from app.models.user import UserFavorite
from app.schemas.news import NewsFilter, NewsOut, NewsUpdateIn, PaginatedResponse
from fastapi import HTTPException, status


class NewsService(INewsService):
    """Concrete implementation of the news business-logic layer."""

    def __init__(self, news_repository: INewsRepository):
        """Initialise the service with a news repository.

        :param news_repository: Concrete repository used for news persistence.
        """
        self._news_repository = news_repository

    async def list_news(
        self, news_filter: NewsFilter, current_user_id: UUID | None
    ) -> PaginatedResponse:
        """Return a paginated feed of articles, annotated with favorite status.

        When ``current_user_id`` is supplied the user's favorited IDs are
        fetched and forwarded to the repository so each article's
        ``is_favorited`` flag is populated correctly.

        :param news_filter: Filter and pagination parameters.
        :param current_user_id: Authenticated user UUID, or ``None`` for guests.
        :return: ``PaginatedResponse`` with articles and pagination metadata.
        """
        from app.repositories.user_repository import UserRepository

        favorited_ids: set[UUID] = set()
        if current_user_id is not None:
            user_repository = UserRepository()
            favorited_ids = await user_repository.get_favorite_news_ids(current_user_id)

        news_items, total = await self._news_repository.find_all(
            news_filter, favorited_ids
        )
        pages = -(-total // news_filter.limit) if news_filter.limit > 0 else 1
        has_next = news_filter.page < pages
        has_previous = news_filter.page > 1

        return PaginatedResponse(
            items=[NewsOut.model_validate(item) for item in news_items],
            total=total,
            page=news_filter.page,
            limit=news_filter.limit,
            pages=pages,
            has_next=has_next,
            has_previous=has_previous,
        )

    async def update_news(self, news_id: UUID, data: NewsUpdateIn) -> NewsOut:
        """Apply a partial update to a news article.

        :param news_id: UUID of the article to update.
        :param data: Fields to patch; ``None`` values are excluded from the update.
        :return: The updated article serialised as ``NewsOut``.
        :raises HTTPException 404: When no article with ``news_id`` exists.
        """
        news = await self._news_repository.find_by_id(news_id)
        if news is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="News article not found"
            )
        updated = await self._news_repository.update(
            news_id, data.model_dump(exclude_none=True)
        )
        return NewsOut.model_validate(updated)

    async def delete_news(self, news_id: UUID) -> None:
        """Permanently delete a news article.

        :param news_id: UUID of the article to delete.
        :raises HTTPException 404: When no article with ``news_id`` exists.
        """
        news = await self._news_repository.find_by_id(news_id)
        if news is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="News article not found"
            )
        await self._news_repository.delete(news_id)

    async def add_favorite(self, news_id: UUID, user_id: UUID) -> None:
        """Save a news article to a user's favorites.

        :param news_id: UUID of the article to favorite.
        :param user_id: UUID of the user who is favoriting.
        :raises HTTPException 404: When no article with ``news_id`` exists.
        :raises HTTPException 409: When the article is already in the user's favorites.
        """
        news = await self._news_repository.find_by_id(news_id)
        if news is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="News article not found"
            )

        is_already_favorited = await UserFavorite.exists(
            user_id=user_id, news_id=news_id
        )
        if is_already_favorited:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="News article already favorited",
            )

        await UserFavorite.create(user_id=user_id, news_id=news_id)

    async def remove_favorite(self, news_id: UUID, user_id: UUID) -> None:
        """Remove a news article from a user's favorites.

        :param news_id: UUID of the article to unfavorite.
        :param user_id: UUID of the user who is unfavoriting.
        :raises HTTPException 404: When the favorite record does not exist.
        """
        deleted_count = await UserFavorite.filter(
            user_id=user_id, news_id=news_id
        ).delete()
        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found"
            )

    async def list_favorites(self, user_id: UUID) -> list[NewsOut]:
        """Retrieve all news articles saved as favorites by the given user.

        Fetches the user's favorited IDs, loads the corresponding articles
        with their categories, and annotates each with ``is_favorited=True``.

        :param user_id: UUID of the user whose favorites to retrieve.
        :return: List of ``NewsOut`` items, each with ``is_favorited=True``.
        """
        from app.models.news import News

        favorite_ids_query = UserFavorite.filter(user_id=user_id).values_list(
            "news_id", flat=True
        )
        favorite_ids = set(await favorite_ids_query)
        news_items = await News.filter(id__in=favorite_ids).prefetch_related("category")
        for item in news_items:
            item.is_favorited = True
        return [NewsOut.model_validate(item) for item in news_items]
