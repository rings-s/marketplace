import base64
import json
from datetime import datetime
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification, NotificationType
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession):
        super().__init__(Notification, session)

    async def list_for_user_cursor(
        self, user_id: UUID, cursor: str | None = None, size: int = 20
    ) -> tuple[list[Notification], str | None, bool]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if cursor:
            try:
                payload = json.loads(base64.urlsafe_b64decode(cursor.encode()))
                cur_time = datetime.fromisoformat(payload["t"])
                stmt = stmt.where(Notification.created_at < cur_time)
            except Exception:
                pass
        stmt = stmt.order_by(Notification.created_at.desc()).limit(size + 1)
        rows = list((await self.session.execute(stmt)).scalars().all())
        has_more = len(rows) > size
        items = rows[:size]
        next_cursor = None
        if has_more and items:
            payload = {"t": items[-1].created_at.isoformat()}
            next_cursor = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
        return items, next_cursor, has_more

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> Notification | None:
        await self.session.execute(
            update(Notification)
            .where(Notification.id == notification_id, Notification.user_id == user_id)
            .values(is_read=True)
        )
        await self.session.flush()
        return await self.get(notification_id)

    async def mark_all_read(self, user_id: UUID) -> int:
        result = await self.session.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .values(is_read=True)
        )
        await self.session.flush()
        return result.rowcount

    async def create_notification(
        self,
        *,
        user_id: UUID,
        type: NotificationType,
        title_ar: str,
        title_en: str,
        body_ar: str,
        body_en: str,
        data: dict | None = None,
    ) -> Notification:
        return await self.create(
            user_id=user_id,
            type=type,
            title_ar=title_ar,
            title_en=title_en,
            body_ar=body_ar,
            body_en=body_en,
            data=data or {},
        )
