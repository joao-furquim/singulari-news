"""Category and user-preference routes.

Provides the public categories listing and authenticated endpoints for
reading and updating the current user's category preferences.
"""

from uuid import UUID

from app.core.dependencies import get_current_user, get_user_repository
from app.interfaces.user_repository import IUserRepository
from app.models.category import Category
from app.schemas.news import CategoryOut
from app.schemas.user import UserOut
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(tags=["preferences"])


class PreferencesIn(BaseModel):
    """Request body for updating user preferences."""

    category_ids: list[UUID]


@router.get("/preferences", response_model=list[CategoryOut])
async def list_categories():
    """List all available news categories. Public endpoint.

    :return: Full list of category objects (id, name, slug, icon, description).
    """
    categories = await Category.all()
    return [CategoryOut.model_validate(c) for c in categories]


@router.get("/users/me/preferences", response_model=list[str])
async def get_my_preferences(
    current_user: UserOut = Depends(get_current_user),
    user_repository: IUserRepository = Depends(get_user_repository),
):
    """Retrieve the authenticated user's category preferences as slug strings.

    Returns slugs (e.g. ``["technology", "ai"]``) rather than UUIDs so the
    frontend can use the values directly in feed filter comparisons and the
    ``GET /news?categories=`` query parameter.

    :return: List of category slug strings.
    :raises HTTPException 401: When the request has no valid Bearer token.
    """
    return await user_repository.get_preference_slugs(current_user.id)


@router.put("/users/me/preferences", response_model=list[UUID])
async def update_my_preferences(
    body: PreferencesIn,
    current_user: UserOut = Depends(get_current_user),
    user_repository: IUserRepository = Depends(get_user_repository),
):
    """Replace the authenticated user's category preferences.

    Deletes all existing preferences and inserts the new set atomically.

    :param body: List of category UUIDs to set as the new preferences.
    :return: The list of stored category UUIDs.
    :raises HTTPException 401: When the request has no valid Bearer token.
    """
    print(f"Preferences payload: {body.category_ids}")
    await user_repository.set_preferences(current_user.id, body.category_ids)
    return body.category_ids
