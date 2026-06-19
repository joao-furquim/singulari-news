from datetime import datetime
from uuid import UUID

from app.models.user import UserRole
from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreateIn(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserUpdateIn(BaseModel):
    name: str | None = None
    locale: str | None = None


class UserInviteIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole


class RoleUpdateIn(BaseModel):
    role: UserRole


class PasswordChangeIn(BaseModel):
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    locale: str
    role: str
    must_change_password: bool = False
    created_at: datetime


class UserPaginatedResponse(BaseModel):
    items: list[UserOut]
    total: int
    page: int
    limit: int
    pages: int
