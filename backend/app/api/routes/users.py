"""User profile and administration routes.

Provides authenticated endpoints for the current user to read and update
their own profile, and admin-only endpoints for managing other users
(listing, inviting, changing roles, and deletion).
"""

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
    """Return the authenticated user's profile.

    :return: The current user's details.
    :raises HTTPException 401: When the request has no valid Bearer token.
    """
    return current_user


@router.put("/users/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    body: PasswordChangeIn,
    current_user: UserOut = Depends(get_current_user),
    auth_service: IUserService = Depends(get_auth_service),
):
    """Update the authenticated user's password and clear the forced-change flag.

    :param body: The new plaintext password.
    :raises HTTPException 401: When the request has no valid Bearer token.
    """
    await auth_service.change_password(current_user.id, body.password)


@router.put("/users/me", response_model=UserOut)
async def update_profile(
    user_data: UserUpdateIn,
    current_user: UserOut = Depends(get_current_user),
    auth_service: IUserService = Depends(get_auth_service),
):
    """Update the authenticated user's profile fields (name, locale).

    :param user_data: Fields to update; omitted fields are left unchanged.
    :return: The updated user profile.
    :raises HTTPException 401: When the request has no valid Bearer token.
    """
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
    """Invite a new user with a specified role. Requires ``admin`` role.

    The created account has ``must_change_password=True``.

    :param user_data: Name, email, initial password, and role for the new user.
    :return: The created user (201 Created).
    :raises HTTPException 401: When the request has no valid Bearer token.
    :raises HTTPException 403: When the caller lacks ``admin`` role, or when
                               attempting to assign the ``root`` role.
    :raises HTTPException 409: When the email address is already registered.
    """
    return await auth_service.invite(user_data)


# ── Admin: user management ────────────────────────────────────────────────────


@router.get("/users", response_model=UserPaginatedResponse)
async def list_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    _: UserOut = Depends(require_role("admin")),
    auth_service: IUserService = Depends(get_auth_service),
):
    """List all non-root users with pagination. Requires ``admin`` role.

    :param page: 1-based page number.
    :param limit: Items per page (1–100).
    :return: Paginated list of users with metadata.
    :raises HTTPException 401: When the request has no valid Bearer token.
    :raises HTTPException 403: When the caller lacks ``admin`` role.
    """
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
    """Retrieve a specific user by UUID. Requires ``admin`` role.

    Root users are excluded from admin visibility.

    :param user_id: UUID of the user to retrieve.
    :return: The user's profile.
    :raises HTTPException 401: When the request has no valid Bearer token.
    :raises HTTPException 403: When the caller lacks ``admin`` role.
    :raises HTTPException 404: When no user with ``user_id`` exists or the
                               user is the root account.
    """
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
    """Change the role of a user. Requires ``admin`` role.

    :param user_id: UUID of the user whose role to change.
    :param body: The new role to assign.
    :return: The updated user profile.
    :raises HTTPException 401: When the request has no valid Bearer token.
    :raises HTTPException 403: When the caller lacks ``admin`` role, when
                               assigning the ``root`` role, or when the
                               target user is the root account.
    :raises HTTPException 404: When no user with ``user_id`` exists.
    """
    return await auth_service.update_user_role(user_id, body.role)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    _: UserOut = Depends(require_role("admin")),
    auth_service: IUserService = Depends(get_auth_service),
):
    """Permanently delete a user account. Requires ``admin`` role.

    :param user_id: UUID of the user to delete.
    :raises HTTPException 401: When the request has no valid Bearer token.
    :raises HTTPException 403: When the caller lacks ``admin`` role or the
                               target user is the root account.
    :raises HTTPException 404: When no user with ``user_id`` exists.
    """
    await auth_service.delete_user(user_id)
