"""News feed routes and favorite management endpoints.

Provides the public news listing endpoint and authenticated routes for
article management (reviewer/admin only) and user favorites.
"""

from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import UUID  # still needed for news_id params

from app.core.dependencies import get_current_user, get_news_service, require_role
from app.interfaces.news_service import INewsService
from app.schemas.news import NewsFilter, NewsOut, NewsUpdateIn, PaginatedResponse
from app.schemas.user import UserOut
from fastapi import APIRouter, Depends, Query, status

router = APIRouter(tags=["news"])


def _resolve_period(period: str) -> tuple[datetime, datetime]:
    """Convert a named period string into an absolute UTC date range.

    :param period: One of ``"day"``, ``"week"``, or ``"month"``.
    :return: Tuple of ``(start_datetime, now)`` in UTC.
    """
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
    categories: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    news_service: INewsService = Depends(get_news_service),
):
    """Retrieve a paginated, filterable news feed. Public endpoint.

    ``period`` is a convenience shorthand that overrides ``date_from``/
    ``date_to`` when provided. ``categories`` is a comma-separated list of
    category slugs (e.g. ``"technology,ai"``).

    :param period: Named time window — ``"day"``, ``"week"``, or ``"month"``.
    :param date_from: Inclusive lower bound for ``published_at`` (ISO 8601).
    :param date_to: Inclusive upper bound for ``published_at`` (ISO 8601).
    :param categories: Comma-separated category slugs to filter by.
    :param page: 1-based page number.
    :param limit: Items per page (1–100).
    :return: Paginated list of news articles with metadata.
    """
    if period is not None:
        date_from, date_to = _resolve_period(period)

    category_slugs: list[str] | None = None
    if categories:
        category_slugs = [c.strip() for c in categories.split(",") if c.strip()] or None
    print(f"Categories filter (slugs): {category_slugs}")

    news_filter = NewsFilter(
        date_from=date_from,
        date_to=date_to,
        categories=category_slugs,
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
    """Partially update a news article. Requires ``reviewer`` or ``admin`` role.

    :param news_id: UUID of the article to update.
    :param body: Fields to patch; omitted fields are left unchanged.
    :return: The updated article.
    :raises HTTPException 401: When the request has no valid Bearer token.
    :raises HTTPException 403: When the user lacks the required role.
    :raises HTTPException 404: When no article with ``news_id`` exists.
    """
    return await news_service.update_news(news_id, body)


@router.delete("/news/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(
    news_id: UUID,
    _: UserOut = Depends(require_role("reviewer", "admin")),
    news_service: INewsService = Depends(get_news_service),
):
    """Permanently delete a news article. Requires ``reviewer`` or ``admin`` role.

    :param news_id: UUID of the article to delete.
    :raises HTTPException 401: When the request has no valid Bearer token.
    :raises HTTPException 403: When the user lacks the required role.
    :raises HTTPException 404: When no article with ``news_id`` exists.
    """
    await news_service.delete_news(news_id)


@router.post("/news/{news_id}/favorite", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    news_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    news_service: INewsService = Depends(get_news_service),
):
    """Save a news article to the authenticated user's favorites.

    :param news_id: UUID of the article to favorite.
    :return: Confirmation message (201 Created).
    :raises HTTPException 401: When the request has no valid Bearer token.
    :raises HTTPException 404: When no article with ``news_id`` exists.
    :raises HTTPException 409: When the article is already in the user's favorites.
    """
    await news_service.add_favorite(news_id, current_user.id)
    return {"detail": "News article added to favorites"}


@router.delete("/news/{news_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    news_id: UUID,
    current_user: UserOut = Depends(get_current_user),
    news_service: INewsService = Depends(get_news_service),
):
    """Remove a news article from the authenticated user's favorites.

    :param news_id: UUID of the article to unfavorite.
    :raises HTTPException 401: When the request has no valid Bearer token.
    :raises HTTPException 404: When the favorite record does not exist.
    """
    await news_service.remove_favorite(news_id, current_user.id)


@router.get("/users/me/favorites", response_model=list[NewsOut])
async def list_favorites(
    current_user: UserOut = Depends(get_current_user),
    news_service: INewsService = Depends(get_news_service),
):
    """Retrieve all news articles saved as favorites by the authenticated user.

    :return: List of favorited articles, each annotated with ``is_favorited=True``.
    :raises HTTPException 401: When the request has no valid Bearer token.
    """
    return await news_service.list_favorites(current_user.id)
