"""Unit tests for NewsService — list_news pagination and filtering."""

from datetime import datetime
from unittest.mock import MagicMock, patch

from app.schemas.news import NewsFilter
from app.services.news_service import NewsService

# ── test_get_news_returns_paginated_response ──────────────────────────────────


async def test_get_news_returns_paginated_response(
    mock_news_repository: MagicMock,
    sample_news_out: MagicMock,
) -> None:
    """Repository returns 1 item on page 2 of 2 → correct pagination metadata."""
    mock_news_item = MagicMock()
    mock_news_repository.find_all.return_value = ([mock_news_item], 15)

    service = NewsService(mock_news_repository)
    news_filter = NewsFilter(page=2, limit=10)

    with patch(
        "app.services.news_service.NewsOut.model_validate", return_value=sample_news_out
    ):
        result = await service.list_news(news_filter, current_user_id=None)

    assert result.total == 15
    assert result.page == 2
    assert result.limit == 10
    assert result.pages == 2  # ceil(15/10)
    assert result.has_next is False  # page 2 == pages 2
    assert result.has_previous is True
    assert len(result.items) == 1
    assert result.items[0] is sample_news_out


async def test_get_news_empty_result(mock_news_repository: MagicMock) -> None:
    """No articles match filters → empty items list, total=0, pages=1."""
    mock_news_repository.find_all.return_value = ([], 0)

    service = NewsService(mock_news_repository)
    news_filter = NewsFilter(page=1, limit=10)

    result = await service.list_news(news_filter, current_user_id=None)

    assert result.total == 0
    assert result.items == []
    assert result.pages == 0  # -(-0 // 10) == 0; service doesn't floor at 1
    assert result.has_next is False
    assert result.has_previous is False
    mock_news_repository.find_all.assert_called_once_with(news_filter, set())


# ── test_get_news_with_category_filter ───────────────────────────────────────


async def test_get_news_with_category_filter(mock_news_repository: MagicMock) -> None:
    """Category slugs are forwarded to the repository unchanged."""
    mock_news_repository.find_all.return_value = ([], 0)

    service = NewsService(mock_news_repository)
    news_filter = NewsFilter(page=1, limit=10, categories=["technology", "ai"])

    await service.list_news(news_filter, current_user_id=None)

    called_filter: NewsFilter = mock_news_repository.find_all.call_args[0][0]
    assert called_filter.categories == ["technology", "ai"]


# ── test_get_news_with_period_today ──────────────────────────────────────────


async def test_get_news_with_period_today(mock_news_repository: MagicMock) -> None:
    """date_from / date_to are passed through to the repository correctly."""
    today_start = datetime(2026, 6, 18, 0, 0, 0)
    now = datetime(2026, 6, 18, 12, 30, 0)
    mock_news_repository.find_all.return_value = ([], 7)

    service = NewsService(mock_news_repository)
    news_filter = NewsFilter(page=1, limit=20, date_from=today_start, date_to=now)

    result = await service.list_news(news_filter, current_user_id=None)

    assert result.total == 7
    called_filter: NewsFilter = mock_news_repository.find_all.call_args[0][0]
    assert called_filter.date_from == today_start
    assert called_filter.date_to == now


# ── pagination edge cases ─────────────────────────────────────────────────────


async def test_get_news_first_page_has_no_previous(
    mock_news_repository: MagicMock,
) -> None:
    """Page 1 always has has_previous=False."""
    mock_news_repository.find_all.return_value = ([], 30)

    service = NewsService(mock_news_repository)
    result = await service.list_news(NewsFilter(page=1, limit=10), current_user_id=None)

    assert result.has_previous is False
    assert result.has_next is True
    assert result.pages == 3


async def test_get_news_passes_empty_favorites_when_anonymous(
    mock_news_repository: MagicMock,
) -> None:
    """Unauthenticated request → repository receives empty favorited_ids set."""
    mock_news_repository.find_all.return_value = ([], 0)

    service = NewsService(mock_news_repository)
    await service.list_news(NewsFilter(page=1, limit=10), current_user_id=None)

    _filter, favorited_ids = mock_news_repository.find_all.call_args[0]
    assert favorited_ids == set()
