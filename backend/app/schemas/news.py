from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    icon: str | None
    description: str | None


class NewsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class NewsUpdateIn(BaseModel):
    title: str | None = None
    source: str | None = None
    summary: str | None = None
    content: str | None = None
    published_at: datetime | None = None


class NewsFilter(BaseModel):
    date_from: datetime | None = None
    date_to: datetime | None = None
    categories: list[str] | None = None  # category slugs
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
