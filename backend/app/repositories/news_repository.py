from uuid import UUID

from app.interfaces.news_repository import INewsRepository
from app.models.news import News
from app.schemas.news import NewsFilter


class NewsRepository(INewsRepository):
    async def find_all(self, news_filter: NewsFilter, favorited_ids: set[UUID]) -> tuple[list[News], int]:
        query = News.all().prefetch_related("category")

        if news_filter.date_from:
            query = query.filter(published_at__gte=news_filter.date_from)
        if news_filter.date_to:
            query = query.filter(published_at__lte=news_filter.date_to)
        if news_filter.categories:
            query = query.filter(category_id__in=news_filter.categories)

        total = await query.count()
        offset = (news_filter.page - 1) * news_filter.limit
        news_items = await query.order_by("-published_at").offset(offset).limit(news_filter.limit)

        for news_item in news_items:
            news_item.is_favorited = news_item.id in favorited_ids

        return news_items, total

    async def find_by_id(self, news_id: UUID) -> News | None:
        return await News.get_or_none(id=news_id).prefetch_related("category")

    async def create(self, news_data: dict) -> News:
        return await News.create(**news_data)

    async def update(self, news_id: UUID, news_data: dict) -> News:
        await News.filter(id=news_id).update(**news_data)
        return await News.get(id=news_id).prefetch_related("category")

    async def delete(self, news_id: UUID) -> None:
        await News.filter(id=news_id).delete()
