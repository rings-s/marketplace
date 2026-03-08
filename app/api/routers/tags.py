from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import CurrentUser
from app.schemas.item import TagResponse
from app.repositories.item import TagRepository
from app.core.enums import UserRole
from app.core.exceptions import ForbiddenError

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagResponse])
async def list_tags(session: AsyncSession = Depends(get_db)):
    repo = TagRepository(session)
    return await repo.list(limit=200)


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(
    name_ar: str,
    name_en: str,
    slug: str,
    category: str | None = None,
    current_user: CurrentUser = None,
    session: AsyncSession = Depends(get_db),
):
    if current_user.role != UserRole.admin:
        raise ForbiddenError("Admin only")
    repo = TagRepository(session)
    return await repo.create(name_ar=name_ar, name_en=name_en, slug=slug, category=category)
