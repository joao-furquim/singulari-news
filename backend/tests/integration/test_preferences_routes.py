"""Integration tests for the public /preferences endpoint."""

from httpx import AsyncClient


async def test_get_preferences_is_public(client: AsyncClient) -> None:
    """No auth token required."""
    response = await client.get("/preferences")
    assert response.status_code == 200


async def test_get_preferences_returns_list(client: AsyncClient) -> None:
    response = await client.get("/preferences")
    assert isinstance(response.json(), list)


async def test_get_preferences_returns_8_categories(client: AsyncClient) -> None:
    response = await client.get("/preferences")
    assert len(response.json()) == 8


async def test_get_preferences_category_structure(client: AsyncClient) -> None:
    """Each category has the required fields."""
    response = await client.get("/preferences")
    for category in response.json():
        assert "id" in category
        assert "name" in category
        assert "slug" in category
        assert "icon" in category


async def test_get_preferences_contains_canonical_slugs(client: AsyncClient) -> None:
    response = await client.get("/preferences")
    slugs = {c["slug"] for c in response.json()}
    expected = {
        "technology",
        "ai",
        "business",
        "science",
        "health",
        "politics",
        "sports",
        "general",
    }
    assert slugs == expected
