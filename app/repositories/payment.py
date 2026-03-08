from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payment import Payment, WebhookEvent
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Payment, session)

    async def get_by_moyasar_id(self, moyasar_payment_id: str) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(Payment.moyasar_payment_id == moyasar_payment_id)
        )
        return result.scalar_one_or_none()

    async def get_webhook_event(self, event_id: str) -> WebhookEvent | None:
        result = await self.session.execute(
            select(WebhookEvent).where(WebhookEvent.id == event_id)
        )
        return result.scalar_one_or_none()

    async def create_webhook_event(self, *, event_id: str, event_type: str) -> WebhookEvent:
        event = WebhookEvent(id=event_id, event_type=event_type)
        self.session.add(event)
        await self.session.flush()
        return event
