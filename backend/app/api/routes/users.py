from uuid import UUID

from app.core.dependencies import get_auth_service, get_current_user, require_role
from app.interfaces.user_service import IUserService
from app.schemas.user import (
    PasswordChangeIn,
    RoleUpdateIn,
    UserInviteIn,
    UserOut,
    UserPaginatedResponse,
    UserUpdateIn,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
import math

router = APIRouter(tags=["users"])


# ── Authenticated user profile ────────────────────────────────────────────────


@router.get("/users/me", response_model=UserOut)
async def get_profile(current_user: UserOut = Depends(get_current_user)):
    return current_user


@router.put("/users/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    body: PasswordChangeIn,
    current_user: UserOut = Depends(get_current_user),
    auth_service: IUserService = Depends(get_auth_service),
):
    await auth_service.change_password(current_user.id, body.password)


@router.put("/users/me", response_model=UserOut)
async def update_profile(
    user_data: UserUpdateIn,
    current_user: UserOut = Depends(get_current_user),
    auth_service: IUserService = Depends(get_auth_service),
):
    return await auth_service.update_profile(current_user.id, user_data)


# ── Invite (admin only) ───────────────────────────────────────────────────────


@router.post(
    "/users/invite", response_model=UserOut, status_code=status.HTTP_201_CREATED
)
async def invite_user(
    user_data: UserInviteIn,
    _: UserOut = Depends(require_role("admin")),
    auth_service: IUserService = Depends(get_auth_service),
):
    return await auth_service.invite(user_data)


# ── Admin: user management ────────────────────────────────────────────────────


@router.get("/users", response_model=UserPaginatedResponse)
async def list_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    _: UserOut = Depends(require_role("admin")),
    auth_service: IUserService = Depends(get_auth_service),
):
    users, total = await auth_service.list_users(page, limit)
    return UserPaginatedResponse(
        items=users,
        total=total,
        page=page,
        limit=limit,
        pages=max(1, math.ceil(total / limit)),
    )


@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(
    user_id: UUID,
    _: UserOut = Depends(require_role("admin")),
    auth_service: IUserService = Depends(get_auth_service),
):
    from app.core.dependencies import get_user_repository
    from app.models.user import UserRole

    repo = get_user_repository()
    user = await repo.find_by_id(user_id)
    if not user or user.role == UserRole.root:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserOut.model_validate(user)


@router.put("/users/{user_id}/role", response_model=UserOut)
async def update_user_role(
    user_id: UUID,
    body: RoleUpdateIn,
    _: UserOut = Depends(require_role("admin")),
    auth_service: IUserService = Depends(get_auth_service),
):
    return await auth_service.update_user_role(user_id, body.role)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    _: UserOut = Depends(require_role("admin")),
    auth_service: IUserService = Depends(get_auth_service),
):
    await auth_service.delete_user(user_id)
