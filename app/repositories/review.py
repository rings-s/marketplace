from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.review import Review
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    def __init__(self, session: AsyncSession):
        super().__init__(Review, session)

    async def get_by_order(self, order_id: UUID) -> Review | None:
        result = await self.session.execute(
            select(Review).where(Review.order_id == order_id)
        )
        return result.scalar_one_or_none()

    async def list_for_reviewee(
        self, reviewee_id: UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[Review], int]:
        stmt = select(Review).where(Review.reviewee_id == reviewee_id)
        count = (await self.session.execute(
            select(func.count()).select_from(stmt.subquery())
        )).scalar_one()
        rows = list((await self.session.execute(
            stmt.order_by(Review.created_at.desc()).offset(offset).limit(limit)
        )).scalars().all())
        return rows, count

    async def avg_rating(self, reviewee_id: UUID) -> float:
        result = await self.session.execute(
            select(func.avg(Review.rating)).where(Review.reviewee_id == reviewee_id)
        )
        val = result.scalar_one_or_none()
        return float(val) if val else 0.0
