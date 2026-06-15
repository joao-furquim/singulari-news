from uuid import UUID

from fastapi import HTTPException, status

from app.interfaces.news_repository import INewsRepository
from app.interfaces.news_service import INewsService
from app.models.user import UserFavorite
from app.schemas.news import NewsFilter, NewsOut, NewsUpdateIn, PaginatedResponse


class NewsService(INewsService):
    def __init__(self, news_repository: INewsRepository):
        self._news_repository = news_repository

    async def list_news(self, news_filter: NewsFilter, current_user_id: UUID | None) -> PaginatedResponse:
        from app.repositories.user_repository import UserRepository

        favorited_ids: set[UUID] = set()
        if current_user_id is not None:
            user_repository = UserRepository()
            favorited_ids = await user_repository.get_favorite_news_ids(current_user_id)

        news_items, total = await self._news_repository.find_all(news_filter, favorited_ids)
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
        news = await self._news_repository.find_by_id(news_id)
        if news is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News article not found")
        updated = await self._news_repository.update(news_id, data.model_dump(exclude_none=True))
        return NewsOut.model_validate(updated)

    async def delete_news(self, news_id: UUID) -> None:
        news = await self._news_repository.find_by_id(news_id)
        if news is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News article not found")
        await self._news_repository.delete(news_id)

    async def add_favorite(self, news_id: UUID, user_id: UUID) -> None:
        news = await self._news_repository.find_by_id(news_id)
        if news is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News article not found")

        is_already_favorited = await UserFavorite.exists(user_id=user_id, news_id=news_id)
        if is_already_favorited:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="News article already favorited")

        await UserFavorite.create(user_id=user_id, news_id=news_id)

    async def remove_favorite(self, news_id: UUID, user_id: UUID) -> None:
        deleted_count = await UserFavorite.filter(user_id=user_id, news_id=news_id).delete()
        if deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")

    async def list_favorites(self, user_id: UUID) -> list[NewsOut]:
        from app.models.news import News
        favorite_ids_query = UserFavorite.filter(user_id=user_id).values_list("news_id", flat=True)
        favorite_ids = set(await favorite_ids_query)
        news_items = await News.filter(id__in=favorite_ids).prefetch_related("category")
        for item in news_items:
            item.is_favorited = True
        return [NewsOut.model_validate(item) for item in news_items]
