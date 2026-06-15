from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: UUID
    name: str
    slug: str
    icon: str | None
    description: str | None

    class Config:
        from_attributes = True


class NewsOut(BaseModel):
    id: UUID
    category: CategoryOut
    title: str
    source: str
    summary: str | None
    content: str
    published_at: datetime
    ai_generated: bool
    created_at: datetime
    is_favorited: bool = False

    class Config:
        from_attributes = True


class NewsUpdateIn(BaseModel):
    title: str | None = None
    source: str | None = None
    summary: str | None = None
    content: str | None = None
    published_at: datetime | None = None


class NewsFilter(BaseModel):
    date_from: datetime | None = None
    date_to: datetime | None = None
    categories: list[UUID] | None = None
    page: int = 1
    limit: int = 20


class PaginatedResponse(BaseModel):
    items: list[NewsOut]
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_previous: bool
