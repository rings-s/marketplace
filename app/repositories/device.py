from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.device import ExpoToken


class DeviceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: UUID) -> ExpoToken | None:
        result = await self.session.execute(
            select(ExpoToken).where(ExpoToken.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, user_id: UUID, token: str) -> ExpoToken:
        existing = await self.get(user_id)
        if existing:
            existing.token = token
            await self.session.flush()
            return existing
        device = ExpoToken(user_id=user_id, token=token)
        self.session.add(device)
        await self.session.flush()
        return device

    async def delete(self, user_id: UUID) -> None:
        await self.session.execute(
            delete(ExpoToken).where(ExpoToken.user_id == user_id)
        )
        await self.session.flush()
