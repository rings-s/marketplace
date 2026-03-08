from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import CurrentUser
from app.schemas.social import ReportCreate, ReportResponse
from app.repositories.social import ReportRepository

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportResponse, status_code=201)
async def create_report(
    body: ReportCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = ReportRepository(session)
    return await repo.create(
        reporter_id=current_user.id,
        target_type=body.target_type,
        target_id=body.target_id,
        reason=body.reason,
    )


@router.get("", response_model=list[ReportResponse])
async def list_reports(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    from app.core.enums import UserRole
    from app.core.exceptions import ForbiddenError
    if current_user.role != UserRole.admin:
        raise ForbiddenError("Admin only")
    repo = ReportRepository(session)
    return await repo.list(limit=100)
