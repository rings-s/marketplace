from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import CurrentUser
from app.schemas.device import DeviceTokenCreate, DeviceTokenResponse
from app.repositories.device import DeviceRepository

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/token", response_model=DeviceTokenResponse)
async def register_token(
    body: DeviceTokenCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = DeviceRepository(session)
    await repo.upsert(current_user.id, body.token)
    return DeviceTokenResponse(registered=True)


@router.delete("/token", response_model=DeviceTokenResponse)
async def remove_token(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = DeviceRepository(session)
    await repo.delete(current_user.id)
    return DeviceTokenResponse(registered=False)
