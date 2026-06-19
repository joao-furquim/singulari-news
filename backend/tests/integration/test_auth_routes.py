"""Integration tests for POST /users (register) and POST /login."""

from httpx import AsyncClient


async def test_register_user_returns_201(client: AsyncClient) -> None:
    response = await client.post(
        "/users",
        json={"name": "New User", "email": "newuser@test.com", "password": "Test@123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["name"] == "New User"
    assert "id" in data
    assert "password_hash" not in data  # never expose the hash


async def test_register_duplicate_email_returns_409(client: AsyncClient) -> None:
    payload = {"name": "Test", "email": "dup@test.com", "password": "Test@123"}
    await client.post("/users", json=payload)
    response = await client.post("/users", json=payload)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


async def test_register_invalid_email_returns_422(client: AsyncClient) -> None:
    response = await client.post(
        "/users",
        json={"name": "Test", "email": "not-an-email", "password": "Test@123"},
    )
    assert response.status_code == 422


async def test_login_success_returns_access_token(client: AsyncClient) -> None:
    response = await client.post(
        "/login",
        json={"email": "admin@singulari.com", "password": "Admin@123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == "admin@singulari.com"
    assert "preferences" in data


async def test_login_wrong_password_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/login",
        json={"email": "admin@singulari.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_login_unknown_email_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/login",
        json={"email": "ghost@nowhere.com", "password": "Test@123"},
    )
    assert response.status_code == 401


async def test_login_with_registered_user(client: AsyncClient) -> None:
    """Full round-trip: register then login with the same credentials."""
    email = "roundtrip@test.com"
    password = "Round@123"
    await client.post(
        "/users", json={"name": "Round Trip", "email": email, "password": password}
    )

    response = await client.post("/login", json={"email": email, "password": password})
    assert response.status_code == 200
    assert response.json()["user"]["email"] == email
