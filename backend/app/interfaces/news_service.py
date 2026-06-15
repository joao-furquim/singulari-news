from abc import ABC, abstractmethod
from uuid import UUID

from app.schemas.news import NewsFilter, NewsOut, NewsUpdateIn, PaginatedResponse


class INewsService(ABC):
    @abstractmethod
    async def list_news(self, news_filter: NewsFilter, current_user_id: UUID | None) -> PaginatedResponse:
        pass

    @abstractmethod
    async def update_news(self, news_id: UUID, data: NewsUpdateIn) -> NewsOut:
        pass

    @abstractmethod
    async def delete_news(self, news_id: UUID) -> None:
        pass

    @abstractmethod
    async def add_favorite(self, news_id: UUID, user_id: UUID) -> None:
        pass

    @abstractmethod
    async def remove_favorite(self, news_id: UUID, user_id: UUID) -> None:
        pass

    @abstractmethod
    async def list_favorites(self, user_id: UUID) -> list:
        pass
