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
    return NewsRepository()


def get_user_repository() -> IUserRepository:
    return UserRepository()


def get_email_service() -> IEmailService:
    return EmailService()


def get_news_service(
    news_repository: INewsRepository = Depends(get_news_repository),
) -> INewsService:
    return NewsService(news_repository)


def get_auth_service(
    user_repository: IUserRepository = Depends(get_user_repository),
    email_service: IEmailService = Depends(get_email_service),
) -> IUserService:
    return AuthService(user_repository, email_service)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_repository: IUserRepository = Depends(get_user_repository),
) -> UserOut:
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
