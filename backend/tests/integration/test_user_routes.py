"""Integration tests for user management routes."""

from httpx import AsyncClient


async def test_get_users_requires_auth(client: AsyncClient) -> None:
    # HTTPBearer returns 401 when no Authorization header is present
    response = await client.get("/users")
    assert response.status_code == 401


async def test_get_users_requires_admin_role(
    client: AsyncClient, user_token: str
) -> None:
    response = await client.get(
        "/users", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403


async def test_get_users_as_admin_returns_200(
    client: AsyncClient, admin_token: str
) -> None:
    response = await client.get(
        "/users", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


async def test_get_users_does_not_expose_root(
    client: AsyncClient, admin_token: str
) -> None:
    """Root user must be hidden from the admin listing."""
    response = await client.get(
        "/users", headers={"Authorization": f"Bearer {admin_token}"}
    )
    users = response.json()["items"]
    assert not any(u["role"] == "root" for u in users)


async def test_get_my_profile_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/users/me")
    assert response.status_code == 401


async def test_get_my_profile_returns_current_user(
    client: AsyncClient, user_token: str
) -> None:
    response = await client.get(
        "/users/me", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "regularuser@test.com"


async def test_get_my_preferences_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/users/me/preferences")
    assert response.status_code == 401


async def test_get_my_preferences_returns_list(
    client: AsyncClient, user_token: str
) -> None:
    response = await client.get(
        "/users/me/preferences",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_update_preferences_saves_category_ids(
    client: AsyncClient, user_token: str
) -> None:
    # Get available categories
    categories_resp = await client.get("/preferences")
    category_ids = [c["id"] for c in categories_resp.json()[:2]]

    response = await client.put(
        "/users/me/preferences",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"category_ids": category_ids},
    )
    assert response.status_code == 200
    saved = response.json()
    assert sorted(saved) == sorted(category_ids)


async def test_update_preferences_replaces_previous(
    client: AsyncClient, user_token: str
) -> None:
    categories_resp = await client.get("/preferences")
    all_ids = [c["id"] for c in categories_resp.json()]

    # Save 3 preferences
    await client.put(
        "/users/me/preferences",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"category_ids": all_ids[:3]},
    )

    # Replace with just 1
    response = await client.put(
        "/users/me/preferences",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"category_ids": [all_ids[0]]},
    )
    assert response.status_code == 200
    assert response.json() == [all_ids[0]]
