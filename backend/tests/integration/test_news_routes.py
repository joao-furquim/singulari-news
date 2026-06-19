"""Integration tests for GET /news endpoint."""

import pytest
from httpx import AsyncClient


async def test_get_news_returns_200(client: AsyncClient) -> None:
    response = await client.get("/news")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "pages" in data
    assert "page" in data
    assert "limit" in data


async def test_get_news_returns_empty_when_no_articles(client: AsyncClient) -> None:
    response = await client.get("/news")
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


async def test_get_news_with_period_filter(client: AsyncClient) -> None:
    # Valid values: day | week | month  (not 'today')
    response = await client.get("/news?period=day")
    assert response.status_code == 200


async def test_get_news_with_category_filter(client: AsyncClient) -> None:
    response = await client.get("/news?categories=technology")
    assert response.status_code == 200
    assert "items" in response.json()


async def test_get_news_pagination_params(client: AsyncClient) -> None:
    response = await client.get("/news?page=1&limit=5")
    data = response.json()
    assert response.status_code == 200
    assert data["page"] == 1
    assert data["limit"] == 5
    assert len(data["items"]) <= 5


async def test_get_news_rejects_invalid_limit(client: AsyncClient) -> None:
    response = await client.get("/news?limit=999")
    assert response.status_code == 422  # limit max is 100


async def test_get_news_with_date_filter(client: AsyncClient) -> None:
    response = await client.get(
        "/news",
        params={
            "date_from": "2026-06-18T00:00:00Z",
            "date_to": "2026-06-18T23:59:59Z",
        },
    )
    assert response.status_code == 200


@pytest.mark.parametrize("page", [1, 2, 3])
async def test_get_news_accepts_any_page(client: AsyncClient, page: int) -> None:
    response = await client.get(f"/news?page={page}")
    assert response.status_code == 200
    assert response.json()["page"] == page
