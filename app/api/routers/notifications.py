from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import CurrentUser
from app.schemas.notification import NotificationResponse, CursorNotificationList
from app.repositories.notification import NotificationRepository
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=CursorNotificationList)
async def list_notifications(
    current_user: CurrentUser,
    cursor: str | None = None,
    size: int = Query(20, ge=1, le=50),
    session: AsyncSession = Depends(get_db),
):
    repo = NotificationRepository(session)
    items, next_cursor, has_more = await repo.list_for_user_cursor(
        current_user.id, cursor=cursor, size=size
    )
    return CursorNotificationList(items=items, next_cursor=next_cursor, has_more=has_more)


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_read(
    notification_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = NotificationRepository(session)
    notif = await repo.mark_read(notification_id, current_user.id)
    if not notif:
        raise NotFoundError("Notification not found")
    return notif


@router.post("/read-all")
async def mark_all_read(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = NotificationRepository(session)
    count = await repo.mark_all_read(current_user.id)
    return {"count": count}
