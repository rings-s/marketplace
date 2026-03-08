from typing import Any, Generic, TypeVar
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: type[ModelT], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: UUID | str) -> ModelT | None:
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_or_404(self, id: UUID | str) -> ModelT:
        from app.core.exceptions import NotFoundError
        obj = await self.get(id)
        if not obj:
            raise NotFoundError(f"{self.model.__name__} not found")
        return obj

    async def create(self, **kwargs: Any) -> ModelT:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: UUID | str, **kwargs: Any) -> ModelT | None:
        await self.session.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )
        await self.session.flush()
        return await self.get(id)

    async def delete(self, id: UUID | str) -> None:
        await self.session.execute(delete(self.model).where(self.model.id == id))

    async def list(self, offset: int = 0, limit: int = 20) -> list[ModelT]:
        result = await self.session.execute(select(self.model).offset(offset).limit(limit))
        return list(result.scalars().all())
