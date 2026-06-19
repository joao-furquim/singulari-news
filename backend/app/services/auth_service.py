from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.core.security import (
    create_access_token,
    create_reset_token,
    hash_password,
    verify_password,
)
from app.interfaces.email_service import IEmailService
from app.interfaces.user_repository import IUserRepository
from app.interfaces.user_service import IUserService
from app.models.user import UserRole
from app.schemas.auth import ForgotPasswordIn, LoginIn, ResetPasswordIn, TokenOut
from app.schemas.user import UserCreateIn, UserInviteIn, UserOut, UserUpdateIn
from fastapi import HTTPException, status


class AuthService(IUserService):
    def __init__(
        self,
        user_repository: IUserRepository,
        email_service: IEmailService,
    ):
        self._user_repository = user_repository
        self._email_service = email_service

    async def register(self, user_data: UserCreateIn) -> UserOut:
        existing_user = await self._user_repository.find_by_email(user_data.email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        new_user = await self._user_repository.create(
            {
                "name": user_data.name,
                "email": user_data.email,
                "password_hash": hash_password(user_data.password),
                "role": UserRole.user,
            }
        )
        return UserOut.model_validate(new_user)

    async def invite(self, user_data: UserInviteIn) -> UserOut:
        if user_data.role == UserRole.root:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create users with root role",
            )
        existing_user = await self._user_repository.find_by_email(user_data.email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        new_user = await self._user_repository.create(
            {
                "name": user_data.name,
                "email": user_data.email,
                "password_hash": hash_password(user_data.password),
                "role": user_data.role,
                "must_change_password": True,
            }
        )
        return UserOut.model_validate(new_user)

    async def login(self, credentials: LoginIn) -> TokenOut:
        user = await self._user_repository.find_by_email(credentials.email)
        is_authenticated = user is not None and verify_password(
            credentials.password, user.password_hash
        )
        if not is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        access_token = create_access_token(str(user.id))
        preferences = await self._user_repository.get_preference_ids(user.id)

        return TokenOut(
            access_token=access_token,
            user=UserOut.model_validate(user),
            preferences=preferences,
        )

    async def forgot_password(self, data: ForgotPasswordIn) -> None:
        user = await self._user_repository.find_by_email(data.email)
        if user is None:
            return

        from app.core.config import settings

        reset_token = create_reset_token(str(user.id))
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_RESET_TOKEN_EXPIRE_MINUTES
        )

        await self._user_repository.save_password_reset(
            {
                "user_id": user.id,
                "token": reset_token,
                "expires_at": expires_at,
            }
        )

        await self._email_service.send_password_reset(user.email, reset_token)

    async def reset_password(self, data: ResetPasswordIn) -> None:
        reset_record = await self._user_repository.find_valid_reset_token(data.token)
        if reset_record is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )

        await self._user_repository.update(
            reset_record.user_id,
            {"password_hash": hash_password(data.new_password)},
        )
        reset_record.is_used = True
        await reset_record.save()

    async def update_profile(self, user_id: UUID, data: UserUpdateIn) -> UserOut:
        update_data = data.model_dump(exclude_none=True)
        updated_user = await self._user_repository.update(user_id, update_data)
        return UserOut.model_validate(updated_user)

    async def list_users(
        self, page: int = 1, limit: int = 10
    ) -> tuple[list[UserOut], int]:
        users, total = await self._user_repository.find_all_paginated(page, limit)
        return [UserOut.model_validate(u) for u in users], total

    async def delete_user(self, user_id: UUID) -> None:
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if user.role == UserRole.root:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Root user cannot be deleted",
            )
        await self._user_repository.delete(user_id)

    async def change_password(self, user_id: UUID, new_password: str) -> None:
        await self._user_repository.update(
            user_id,
            {
                "password_hash": hash_password(new_password),
                "must_change_password": False,
            },
        )

    async def update_user_role(self, user_id: UUID, role: UserRole) -> UserOut:
        if role == UserRole.root:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot assign root role",
            )
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if user.role == UserRole.root:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Root user role cannot be changed",
            )
        updated_user = await self._user_repository.update(user_id, {"role": role})
        return UserOut.model_validate(updated_user)
