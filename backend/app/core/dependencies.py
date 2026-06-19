"""FastAPI dependency functions for injecting services and enforcing auth.

All injectable dependencies follow the ``get_*`` naming convention.
``get_current_user`` and ``require_role`` are used as security guards on
protected routes. Concrete repository and service instances are created
here and wired together.
"""

from uuid import UUID

from app.core.security import decode_token
from app.interfaces.email_service import IEmailService
from app.interfaces.news_repository import INewsRepository
from app.interfaces.news_service import INewsService
from app.interfaces.user_repository import IUserRepository
from app.interfaces.user_service import IUserService
from app.repositories.news_repository import NewsRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserOut
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.news_service import NewsService
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

bearer_scheme = HTTPBearer()


def get_news_repository() -> INewsRepository:
    """Provide a concrete ``NewsRepository`` instance.

    :return: A new ``NewsRepository`` backed by Tortoise ORM.
    """
    return NewsRepository()


def get_user_repository() -> IUserRepository:
    """Provide a concrete ``UserRepository`` instance.

    :return: A new ``UserRepository`` backed by Tortoise ORM.
    """
    return UserRepository()


def get_email_service() -> IEmailService:
    """Provide a concrete ``EmailService`` instance.

    :return: A new ``EmailService`` backed by Resend (falls back to logging
             when ``RESEND_API_KEY`` is empty).
    """
    return EmailService()


def get_news_service(
    news_repository: INewsRepository = Depends(get_news_repository),
) -> INewsService:
    """Provide a ``NewsService`` wired with its repository dependency.

    :param news_repository: Injected news repository instance.
    :return: A new ``NewsService``.
    """
    return NewsService(news_repository)


def get_auth_service(
    user_repository: IUserRepository = Depends(get_user_repository),
    email_service: IEmailService = Depends(get_email_service),
) -> IUserService:
    """Provide an ``AuthService`` wired with its repository and email dependencies.

    :param user_repository: Injected user repository instance.
    :param email_service: Injected email service instance.
    :return: A new ``AuthService``.
    """
    return AuthService(user_repository, email_service)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_repository: IUserRepository = Depends(get_user_repository),
) -> UserOut:
    """Validate the Bearer token and return the authenticated user.

    Decodes the JWT, verifies it is an ``access`` token, and loads the
    corresponding user from the database.

    :param credentials: HTTP Bearer credentials extracted from the
                        ``Authorization`` header.
    :param user_repository: Injected user repository for the user look-up.
    :return: The authenticated user serialised as ``UserOut``.
    :raises HTTPException 401: When the token is missing, invalid, expired,
                               or does not belong to an existing user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_repository.find_by_id(UUID(user_id))
    if user is None:
        raise credentials_exception
    return UserOut.model_validate(user)


def require_role(*roles: str):
    """Return a FastAPI dependency that enforces role-based access control.

    The ``root`` role implicitly satisfies any role requirement. All other
    users must have one of the explicitly listed roles.

    :param roles: One or more role strings the caller must possess
                  (e.g. ``"admin"``, ``"reviewer"``).
    :return: An async dependency function that resolves to the current user
             or raises 403.
    :raises HTTPException 403: When the authenticated user's role is not in
                               the allowed set.
    """

    async def check_role(current_user: UserOut = Depends(get_current_user)) -> UserOut:
        if current_user.role == "root":  # root inherits all permissions
            return current_user
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(roles)}",
            )
        return current_user

    return check_role
