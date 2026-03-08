from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.social import Order
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def list_for_user(self, user_id: UUID) -> list[Order]:
        result = await self.session.execute(
            select(Order).where(
                (Order.buyer_id == user_id) | (Order.seller_id == user_id)
            ).order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())
