from abc import ABC, abstractmethod
from uuid import UUID

from app.models.user import UserRole
from app.schemas.auth import ForgotPasswordIn, LoginIn, ResetPasswordIn, TokenOut
from app.schemas.user import UserCreateIn, UserInviteIn, UserOut, UserUpdateIn


class IUserService(ABC):
    @abstractmethod
    async def register(self, user_data: UserCreateIn) -> UserOut:
        pass

    @abstractmethod
    async def invite(self, user_data: UserInviteIn) -> UserOut:
        pass

    @abstractmethod
    async def login(self, credentials: LoginIn) -> TokenOut:
        pass

    @abstractmethod
    async def forgot_password(self, data: ForgotPasswordIn) -> None:
        pass

    @abstractmethod
    async def reset_password(self, data: ResetPasswordIn) -> None:
        pass

    @abstractmethod
    async def update_profile(self, user_id: UUID, data: UserUpdateIn) -> UserOut:
        pass

    @abstractmethod
    async def update_avatar(self, user_id: UUID, file_bytes: bytes, content_type: str) -> UserOut:
        pass

    @abstractmethod
    async def list_users(self) -> list[UserOut]:
        pass

    @abstractmethod
    async def delete_user(self, user_id: UUID) -> None:
        pass

    @abstractmethod
    async def update_user_role(self, user_id: UUID, role: UserRole) -> UserOut:
        pass
