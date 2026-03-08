from uuid import UUID
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import NotificationType
from app.repositories.notification import NotificationRepository
from app.repositories.device import DeviceRepository

logger = structlog.get_logger()


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self.notif_repo = NotificationRepository(session)
        self.device_repo = DeviceRepository(session)

    async def notify(
        self,
        *,
        user_id: UUID,
        type: NotificationType,
        title_ar: str,
        title_en: str,
        body_ar: str,
        body_en: str,
        data: dict | None = None,
        enqueue_push: bool = True,
    ) -> None:
        """Create notification record and optionally enqueue Expo push."""
        await self.notif_repo.create_notification(
            user_id=user_id,
            type=type,
            title_ar=title_ar,
            title_en=title_en,
            body_ar=body_ar,
            body_en=body_en,
            data=data or {},
        )

        if enqueue_push:
            device = await self.device_repo.get(user_id)
            if device:
                try:
                    from arq import create_pool
                    from arq.connections import RedisSettings
                    from app.config import settings
                    pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
                    await pool.enqueue_job(
                        "send_expo_push",
                        device.token,
                        title_en,
                        body_en,
                        data or {},
                    )
                    await pool.aclose()
                except Exception as e:
                    logger.warning("push_enqueue_failed", error=str(e))
