from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.social import Favorite, Report, Order
from app.repositories.base import BaseRepository


class FavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: UUID, item_id: UUID) -> Favorite | None:
        result = await self.session.execute(
            select(Favorite).where(
                and_(Favorite.user_id == user_id, Favorite.item_id == item_id)
            )
        )
        return result.scalar_one_or_none()

    async def add(self, user_id: UUID, item_id: UUID) -> Favorite:
        fav = Favorite(user_id=user_id, item_id=item_id)
        self.session.add(fav)
        await self.session.flush()
        return fav

    async def remove(self, user_id: UUID, item_id: UUID) -> None:
        from sqlalchemy import delete
        await self.session.execute(
            delete(Favorite).where(
                and_(Favorite.user_id == user_id, Favorite.item_id == item_id)
            )
        )
        await self.session.flush()

    async def list_by_user(self, user_id: UUID) -> list[Favorite]:
        result = await self.session.execute(
            select(Favorite).where(Favorite.user_id == user_id)
        )
        return list(result.scalars().all())


class ReportRepository(BaseRepository[Report]):
    def __init__(self, session: AsyncSession):
        super().__init__(Report, session)


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def get_by_item_and_buyer(self, item_id: UUID, buyer_id: UUID) -> Order | None:
        result = await self.session.execute(
            select(Order).where(
                and_(Order.item_id == item_id, Order.buyer_id == buyer_id)
            )
        )
        return result.scalar_one_or_none()
