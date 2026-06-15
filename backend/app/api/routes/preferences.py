from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_user_repository
from app.interfaces.user_repository import IUserRepository
from app.models.category import Category
from app.schemas.news import CategoryOut
from app.schemas.user import UserOut

router = APIRouter(tags=["preferences"])


@router.get("/preferences", response_model=list[CategoryOut])
async def list_categories():
    categories = await Category.all()
    return [CategoryOut.model_validate(c) for c in categories]


@router.get("/users/me/preferences", response_model=list[UUID])
async def get_my_preferences(
    current_user: UserOut = Depends(get_current_user),
    user_repository: IUserRepository = Depends(get_user_repository),
):
    return await user_repository.get_preference_ids(current_user.id)


@router.put("/users/me/preferences", response_model=list[UUID])
async def update_my_preferences(
    category_ids: list[UUID],
    current_user: UserOut = Depends(get_current_user),
    user_repository: IUserRepository = Depends(get_user_repository),
):
    await user_repository.set_preferences(current_user.id, category_ids)
    return category_ids
