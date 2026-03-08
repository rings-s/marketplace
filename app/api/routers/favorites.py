from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import CurrentUser
from app.schemas.social import FavoriteResponse
from app.repositories.social import FavoriteRepository
from app.core.exceptions import ConflictError, NotFoundError

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteResponse])
async def list_favorites(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = FavoriteRepository(session)
    return await repo.list_by_user(current_user.id)


@router.post("/{item_id}", response_model=FavoriteResponse, status_code=201)
async def add_favorite(
    item_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = FavoriteRepository(session)
    existing = await repo.get(current_user.id, item_id)
    if existing:
        raise ConflictError("Already in favorites")
    return await repo.add(current_user.id, item_id)


@router.delete("/{item_id}", status_code=204)
async def remove_favorite(
    item_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = FavoriteRepository(session)
    existing = await repo.get(current_user.id, item_id)
    if not existing:
        raise NotFoundError("Not in favorites")
    await repo.remove(current_user.id, item_id)
