from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import UUID

from app.core.dependencies import get_current_user, get_news_service, require_role
from app.interfaces.news_service import INewsService
from app.schemas.news import NewsFilter, NewsOut, NewsUpdateIn, PaginatedResponse
from app.schemas.user import UserOut
from fastapi import APIRouter, Depends, Query, status

router = APIRouter(tags=["news"])


def _resolve_period(period: str) -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "day":
        return today_start, now
    if period == "week":
        return today_start - timedelta(days=today_start.weekday()), now
    # month
    return today_start.replace(day=1), now


@router.get("/news", response_model=PaginatedResponse)
async def list_news(
    period: Literal["day", "week", "month"] | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    categories: list[UUID] | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    news_service: INewsService = Depends(get_news_service),
):
    if period is not None:
        date_from, date_to = _resolve_period(period)

    news_filter = NewsFilter(
        date_from=date_from,
        date_to=date_to,
        categories=categories,
        page=page,
        limit=limit,
    )
    return await news_service.list_news(news_filter, current_user_id=None)


@router.put("/news/{news_id}", response_model=NewsOut)
async def update_news(
    news_id: UUID,
    body: NewsUpdateIn,
    _: UserOut = Depends(require_role("reviewer", "admin")),
    news_service: INewsService = Depends(get_news_service),
):
    return await news_service.update_news(news_id, body)


@router.delete("/news/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(
    news_id: UUID,
    _: UserOut = Depends(require_role("reviewer", "admin")),
    news_service: INewsService = Depends(get_news_service),
):
    await news_service.delete_news(news_id)


@router.post("/news/{news_id}/favorite", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    news_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    news_service: INewsService = Depends(get_news_service),
):
    await news_service.add_favorite(news_id, current_user.id)
    return {"detail": "News article added to favorites"}


@router.delete("/news/{news_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    news_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    news_service: INewsService = Depends(get_news_service),
):
    await news_service.remove_favorite(news_id, current_user.id)


@router.get("/users/me/favorites", response_model=list[NewsOut])
async def list_favorites(
    current_user: UserOut = Depends(get_current_user),
    news_service: INewsService = Depends(get_news_service),
):
    return await news_service.list_favorites(current_user.id)
