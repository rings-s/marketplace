from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.offer import PriceOffer, OfferStatus
from app.repositories.base import BaseRepository


class OfferRepository(BaseRepository[PriceOffer]):
    def __init__(self, session: AsyncSession):
        super().__init__(PriceOffer, session)

    async def get_pending_for_order(self, order_id: UUID) -> PriceOffer | None:
        result = await self.session.execute(
            select(PriceOffer).where(
                PriceOffer.order_id == order_id,
                PriceOffer.status == OfferStatus.pending,
            )
        )
        return result.scalar_one_or_none()

    async def supersede_pending(self, order_id: UUID) -> None:
        await self.session.execute(
            update(PriceOffer)
            .where(PriceOffer.order_id == order_id, PriceOffer.status == OfferStatus.pending)
            .values(status=OfferStatus.superseded)
        )
        await self.session.flush()

    async def list_for_order(self, order_id: UUID) -> list[PriceOffer]:
        result = await self.session.execute(
            select(PriceOffer)
            .where(PriceOffer.order_id == order_id)
            .order_by(PriceOffer.created_at.desc())
        )
        return list(result.scalars().all())
