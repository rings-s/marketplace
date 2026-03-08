from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.store import Store
from app.repositories.base import BaseRepository


class StoreRepository(BaseRepository[Store]):
    def __init__(self, session: AsyncSession):
        super().__init__(Store, session)

    async def get_by_owner(self, owner_user_id: UUID) -> Store | None:
        result = await self.session.execute(
            select(Store).where(Store.owner_user_id == owner_user_id)
        )
        return result.scalar_one_or_none()
