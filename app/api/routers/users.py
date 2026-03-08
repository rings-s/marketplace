from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import CurrentUser
from app.schemas.user import UserResponse, UserUpdate
from app.repositories.user import UserRepository

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = UserRepository(session)
    updates = body.model_dump(exclude_none=True)
    if updates:
        await repo.update(current_user.id, **updates)
    return await repo.get(current_user.id)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, session: AsyncSession = Depends(get_db)):
    repo = UserRepository(session)
    return await repo.get_or_404(user_id)
