from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status

from app.core.security import (
    create_access_token,
    create_reset_token,
    hash_password,
    verify_password,
)
from app.interfaces.email_service import IEmailService
from app.interfaces.storage_service import IStorageService
from app.interfaces.user_repository import IUserRepository
from app.interfaces.user_service import IUserService
from app.models.user import UserRole
from app.schemas.auth import ForgotPasswordIn, LoginIn, ResetPasswordIn, TokenOut
from app.schemas.user import UserCreateIn, UserInviteIn, UserOut, UserUpdateIn


class AuthService(IUserService):
    def __init__(
        self,
        user_repository: IUserRepository,
        email_service: IEmailService,
        storage_service: IStorageService,
    ):
        self._user_repository = user_repository
        self._email_service = email_service
        self._storage_service = storage_service

    async def register(self, user_data: UserCreateIn) -> UserOut:
        existing_user = await self._user_repository.find_by_email(user_data.email)
        if existing_user is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        new_user = await self._user_repository.create({
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": hash_password(user_data.password),
            "role": UserRole.user,
        })
        return UserOut.model_validate(new_user)

    async def invite(self, user_data: UserInviteIn) -> UserOut:
        existing_user = await self._user_repository.find_by_email(user_data.email)
        if existing_user is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        new_user = await self._user_repository.create({
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": hash_password(user_data.password),
            "role": user_data.role,
        })
        return UserOut.model_validate(new_user)

    async def login(self, credentials: LoginIn) -> TokenOut:
        user = await self._user_repository.find_by_email(credentials.email)
        is_authenticated = user is not None and verify_password(credentials.password, user.password_hash)
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

        await self._user_repository.save_password_reset({
            "user_id": user.id,
            "token": reset_token,
            "expires_at": expires_at,
        })

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

    async def update_avatar(self, user_id: UUID, file_bytes: bytes, content_type: str) -> UserOut:
        avatar_key = f"avatars/{user_id}"
        avatar_url = await self._storage_service.upload(avatar_key, file_bytes, content_type)
        updated_user = await self._user_repository.update(user_id, {"avatar_url": avatar_url})
        return UserOut.model_validate(updated_user)

    async def list_users(self) -> list[UserOut]:
        users = await self._user_repository.find_all()
        return [UserOut.model_validate(u) for u in users]

    async def delete_user(self, user_id: UUID) -> None:
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        await self._user_repository.delete(user_id)

    async def update_user_role(self, user_id: UUID, role: UserRole) -> UserOut:
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        updated_user = await self._user_repository.update(user_id, {"role": role})
        return UserOut.model_validate(updated_user)
