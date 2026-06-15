from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.core.dependencies import get_auth_service, get_current_user, require_role
from app.interfaces.user_service import IUserService
from app.schemas.user import RoleUpdateIn, UserInviteIn, UserOut, UserUpdateIn

router = APIRouter(tags=["users"])


# ── Authenticated user profile ────────────────────────────────────────────────

@router.get("/users/me", response_model=UserOut)
async def get_profile(current_user: UserOut = Depends(get_current_user)):
    return current_user


@router.put("/users/me", response_model=UserOut)
async def update_profile(
    user_data: UserUpdateIn,
    current_user: UserOut = Depends(get_current_user),
    auth_service: IUserService = Depends(get_auth_service),
):
    return await auth_service.update_profile(current_user.id, user_data)


@router.post("/users/me/avatar", response_model=UserOut)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: UserOut = Depends(get_current_user),
    auth_service: IUserService = Depends(get_auth_service),
):
    file_bytes = await file.read()
    return await auth_service.update_avatar(current_user.id, file_bytes, file.content_type)


# ── Invite (admin only) ───────────────────────────────────────────────────────

@router.post("/users/invite", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def invite_user(
    user_data: UserInviteIn,
    _: UserOut = Depends(require_role("admin")),
    auth_service: IUserService = Depends(get_auth_service),
):
    return await auth_service.invite(user_data)


# ── Admin: user management ────────────────────────────────────────────────────

@router.get("/users", response_model=list[UserOut])
async def list_users(
    _: UserOut = Depends(require_role("admin")),
    auth_service: IUserService = Depends(get_auth_service),
):
    return await auth_service.list_users()


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
