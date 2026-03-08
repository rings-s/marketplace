from decimal import Decimal
from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.item import FurnitureItem, Tag, FurnitureItemTag
from app.core.enums import ItemCondition, ItemStatus, SellerType
from app.repositories.base import BaseRepository


class ItemRepository(BaseRepository[FurnitureItem]):
    def __init__(self, session: AsyncSession):
        super().__init__(FurnitureItem, session)

    async def list_with_filters(
        self,
        *,
        city: str | None = None,
        category: str | None = None,
        condition: ItemCondition | None = None,
        status: ItemStatus = ItemStatus.active,
        seller_type: SellerType | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        q: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[FurnitureItem], int]:
        stmt = select(FurnitureItem).where(FurnitureItem.status == status)

        if city:
            stmt = stmt.where(FurnitureItem.location_city == city)
        if category:
            stmt = stmt.where(FurnitureItem.category_main == category)
        if condition:
            stmt = stmt.where(FurnitureItem.condition == condition)
        if seller_type:
            stmt = stmt.where(FurnitureItem.seller_type == seller_type)
        if min_price is not None:
            stmt = stmt.where(FurnitureItem.price_sar >= min_price)
        if max_price is not None:
            stmt = stmt.where(FurnitureItem.price_sar <= max_price)
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    FurnitureItem.title_ar.ilike(pattern),
                    FurnitureItem.title_en.ilike(pattern),
                )
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(FurnitureItem.created_at.desc()).offset(offset).limit(limit)
        rows = (await self.session.execute(stmt)).scalars().all()
        return list(rows), total

    async def increment_views(self, item_id: UUID) -> None:
        item = await self.get(item_id)
        if item:
            item.views_count += 1
            await self.session.flush()

    async def get_tags(self, item_id: UUID) -> list[Tag]:
        stmt = (
            select(Tag)
            .join(FurnitureItemTag, FurnitureItemTag.tag_id == Tag.id)
            .where(FurnitureItemTag.item_id == item_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def set_tags(self, item_id: UUID, tag_ids: list[UUID]) -> None:
        from sqlalchemy import delete
        await self.session.execute(
            delete(FurnitureItemTag).where(FurnitureItemTag.item_id == item_id)
        )
        for tag_id in tag_ids:
            self.session.add(FurnitureItemTag(item_id=item_id, tag_id=tag_id))
        await self.session.flush()


class TagRepository(BaseRepository[Tag]):
    def __init__(self, session: AsyncSession):
        super().__init__(Tag, session)

    async def get_by_slug(self, slug: str) -> Tag | None:
        result = await self.session.execute(select(Tag).where(Tag.slug == slug))
        return result.scalar_one_or_none()
