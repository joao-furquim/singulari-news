"""Unit tests for AuthService — register and login flows."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.schemas.auth import LoginIn
from app.schemas.user import UserCreateIn
from app.services.auth_service import AuthService
from tests.conftest import make_db_user_mock

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_service(
    user_repo: MagicMock,
    email_svc: MagicMock,
) -> AuthService:
    return AuthService(user_repo, email_svc)


# ── register() ────────────────────────────────────────────────────────────────


async def test_register_success(
    mock_user_repository: MagicMock, mock_email_service: MagicMock
) -> None:
    """New email → creates user and returns UserOut."""
    mock_user_repository.find_by_email.return_value = None
    new_db_user = make_db_user_mock(email="new@test.com", name="New User")
    mock_user_repository.create.return_value = new_db_user

    service = _make_service(mock_user_repository, mock_email_service)
    user_data = UserCreateIn(
        name="New User", email="new@test.com", password="Pass@123!"
    )

    result = await service.register(user_data)

    assert result.email == "new@test.com"
    assert result.name == "New User"
    mock_user_repository.find_by_email.assert_called_once_with("new@test.com")
    mock_user_repository.create.assert_called_once()
    create_payload = mock_user_repository.create.call_args[0][0]
    assert create_payload["email"] == "new@test.com"
    assert "password_hash" in create_payload


async def test_register_duplicate_email(
    mock_user_repository: MagicMock, mock_email_service: MagicMock
) -> None:
    """Email already taken → HTTPException 409."""
    mock_user_repository.find_by_email.return_value = make_db_user_mock()

    service = _make_service(mock_user_repository, mock_email_service)
    user_data = UserCreateIn(name="Any", email="taken@test.com", password="Pass@123!")

    with pytest.raises(HTTPException) as exc_info:
        await service.register(user_data)

    assert exc_info.value.status_code == 409
    assert "already registered" in exc_info.value.detail.lower()
    mock_user_repository.create.assert_not_called()


# ── login() ───────────────────────────────────────────────────────────────────


async def test_login_success(
    mock_user_repository: MagicMock, mock_email_service: MagicMock
) -> None:
    """Valid credentials → TokenOut with access_token, user and preferences."""
    db_user = make_db_user_mock(email="user@test.com", password_hash="stored_hash")
    mock_user_repository.find_by_email.return_value = db_user
    mock_user_repository.get_preference_ids.return_value = []

    service = _make_service(mock_user_repository, mock_email_service)
    credentials = LoginIn(email="user@test.com", password="correct_pw")

    with (
        patch(
            "app.services.auth_service.verify_password", return_value=True
        ) as mock_vp,
        patch("app.services.auth_service.create_access_token", return_value="tok123"),
    ):
        result = await service.login(credentials)

    assert result.access_token == "tok123"
    assert result.token_type == "bearer"
    assert result.user.email == "user@test.com"
    assert result.preferences == []
    mock_vp.assert_called_once_with("correct_pw", "stored_hash")


async def test_login_invalid_password(
    mock_user_repository: MagicMock, mock_email_service: MagicMock
) -> None:
    """User exists but password is wrong → HTTPException 401."""
    db_user = make_db_user_mock(password_hash="stored_hash")
    mock_user_repository.find_by_email.return_value = db_user

    service = _make_service(mock_user_repository, mock_email_service)
    credentials = LoginIn(email="user@test.com", password="wrong_pw")

    with patch("app.services.auth_service.verify_password", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await service.login(credentials)

    assert exc_info.value.status_code == 401
    assert "Invalid credentials" in exc_info.value.detail


async def test_login_user_not_found(
    mock_user_repository: MagicMock, mock_email_service: MagicMock
) -> None:
    """No user with that email → HTTPException 401 (same message, no enumeration)."""
    mock_user_repository.find_by_email.return_value = None

    service = _make_service(mock_user_repository, mock_email_service)
    credentials = LoginIn(email="ghost@test.com", password="any_pw")

    with pytest.raises(HTTPException) as exc_info:
        await service.login(credentials)

    assert exc_info.value.status_code == 401
    # verify_password must NOT have been called with None
    mock_user_repository.get_preference_ids.assert_not_called()
