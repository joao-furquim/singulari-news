"""Authentication routes for user registration, login, and password reset.

All endpoints in this module are public (no JWT required). The login
response includes an access token that must be included as a Bearer token
in subsequent requests to protected routes.
"""

from app.core.dependencies import get_auth_service
from app.interfaces.user_service import IUserService
from app.schemas.auth import ForgotPasswordIn, LoginIn, ResetPasswordIn, TokenOut
from app.schemas.user import UserCreateIn, UserOut
from fastapi import APIRouter, Depends, status

router = APIRouter(tags=["auth"])


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreateIn,
    auth_service: IUserService = Depends(get_auth_service),
):
    """Register a new user account.

    :param user_data: Name, email address, and plaintext password.
    :return: The created user (201 Created).
    :raises HTTPException 409: When the email address is already registered.
    """
    return await auth_service.register(user_data)


@router.post("/login", response_model=TokenOut)
async def login(
    credentials: LoginIn,
    auth_service: IUserService = Depends(get_auth_service),
):
    """Authenticate a user and issue a JWT access token.

    :param credentials: Email and plaintext password.
    :return: Access token, token type, user details, and category preference IDs.
    :raises HTTPException 401: When the email or password is incorrect.
    """
    return await auth_service.login(credentials)


@router.post("/auth/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(
    data: ForgotPasswordIn,
    auth_service: IUserService = Depends(get_auth_service),
):
    """Initiate a password-reset flow by sending a reset email.

    Always returns 204 regardless of whether the email is registered
    to prevent user-enumeration attacks.

    :param data: Email address for which a reset is requested.
    """
    await auth_service.forgot_password(data)


@router.post("/auth/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    data: ResetPasswordIn,
    auth_service: IUserService = Depends(get_auth_service),
):
    """Complete a password-reset using a previously issued token.

    :param data: One-time reset token and the new plaintext password.
    :raises HTTPException 400: When the token is invalid, expired, or already used.
    """
    await auth_service.reset_password(data)
