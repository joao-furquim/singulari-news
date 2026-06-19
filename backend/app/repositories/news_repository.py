"""Concrete news repository using Tortoise ORM.

Implements ``INewsRepository`` against the ``news`` and ``categories`` tables.
Filters are applied as chainable queryset constraints; pagination is handled
via offset/limit derived from the ``NewsFilter`` schema.
"""

from uuid import UUID

from app.interfaces.news_repository import INewsRepository
from app.models.news import News
from app.schemas.news import NewsFilter


class NewsRepository(INewsRepository):
    """Tortoise ORM implementation of the news persistence layer."""

    async def find_all(
        self, news_filter: NewsFilter, favorited_ids: set[UUID]
    ) -> tuple[list[News], int]:
        """Retrieve a paginated, filtered list of news articles.

        Applies date-range and category-slug filters to the base queryset,
        counts total matching rows, then fetches the requested page ordered
        by ``published_at`` descending.  Each article is annotated with
        ``is_favorited`` based on ``favorited_ids``.

        :param news_filter: Date range, category slugs, page, and limit.
        :param favorited_ids: Set of news UUIDs the current user has favorited.
        :return: Tuple of ``(news_items, total_count)``.
        """
        query = News.all().prefetch_related("category")

        if news_filter.date_from:
            query = query.filter(published_at__gte=news_filter.date_from)
        if news_filter.date_to:
            query = query.filter(published_at__lte=news_filter.date_to)
        if news_filter.categories:
            query = query.filter(category__slug__in=news_filter.categories)

        total = await query.count()
        offset = (news_filter.page - 1) * news_filter.limit
        news_items = (
            await query.order_by("-published_at")
            .offset(offset)
            .limit(news_filter.limit)
        )

        for news_item in news_items:
            news_item.is_favorited = news_item.id in favorited_ids

        return news_items, total

    async def find_by_id(self, news_id: UUID) -> News | None:
        """Retrieve a single news article by its UUID, including its category.

        :param news_id: UUID of the article to look up.
        :return: The ``News`` instance with ``category`` pre-fetched,
                 or ``None`` if not found.
        """
        return await News.get_or_none(id=news_id).prefetch_related("category")

    async def create(self, news_data: dict) -> News:
        """Persist a new news article.

        :param news_data: Field values for the new record.
        :return: The newly created ``News`` instance.
        """
        return await News.create(**news_data)

    async def update(self, news_id: UUID, news_data: dict) -> News:
        """Apply a partial update to a news article and return the refreshed record.

        :param news_id: UUID of the article to update.
        :param news_data: Fields to patch.
        :return: The updated ``News`` instance with ``category`` pre-fetched.
        """
        await News.filter(id=news_id).update(**news_data)
        return await News.get(id=news_id).prefetch_related("category")

    async def delete(self, news_id: UUID) -> None:
        """Delete a news article by its UUID.

        :param news_id: UUID of the article to delete.
        """
        await News.filter(id=news_id).delete()
