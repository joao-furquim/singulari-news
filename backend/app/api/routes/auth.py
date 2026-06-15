from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_auth_service
from app.interfaces.user_service import IUserService
from app.schemas.auth import ForgotPasswordIn, LoginIn, ResetPasswordIn, TokenOut
from app.schemas.user import UserCreateIn, UserOut

router = APIRouter(tags=["auth"])


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreateIn,
    auth_service: IUserService = Depends(get_auth_service),
):
    return await auth_service.register(user_data)


@router.post("/login", response_model=TokenOut)
async def login(
    credentials: LoginIn,
    auth_service: IUserService = Depends(get_auth_service),
):
    return await auth_service.login(credentials)


@router.post("/auth/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(
    data: ForgotPasswordIn,
    auth_service: IUserService = Depends(get_auth_service),
):
    await auth_service.forgot_password(data)


@router.post("/auth/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    data: ResetPasswordIn,
    auth_service: IUserService = Depends(get_auth_service),
):
    await auth_service.reset_password(data)
