from abc import ABC, abstractmethod
from uuid import UUID

from app.models.news import News
from app.schemas.news import NewsFilter


class INewsRepository(ABC):
    @abstractmethod
    async def find_all(
        self, news_filter: NewsFilter, favorited_ids: set[UUID]
    ) -> tuple[list[News], int]:
        pass

    @abstractmethod
    async def find_by_id(self, news_id: UUID) -> News | None:
        pass

    @abstractmethod
    async def create(self, news_data: dict) -> News:
        pass

    @abstractmethod
    async def update(self, news_id: UUID, news_data: dict) -> News:
        pass

    @abstractmethod
    async def delete(self, news_id: UUID) -> None:
        pass
