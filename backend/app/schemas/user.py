from datetime import datetime
from uuid import UUID

from app.models.user import UserRole
from pydantic import BaseModel, EmailStr


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


class UserOut(BaseModel):
    id: UUID
    name: str
    email: str
    avatar_url: str | None
    locale: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
