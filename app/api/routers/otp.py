from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import CurrentUser
from app.schemas.otp import OTPSendRequest, OTPSendResponse, OTPVerifyRequest, OTPVerifyResponse
from app.services.otp import OTPService
from app.repositories.user import UserRepository
from app.core.exceptions import ValidationError

router = APIRouter(prefix="/otp", tags=["otp"])


@router.post("/send", response_model=OTPSendResponse)
async def send_otp(body: OTPSendRequest, current_user: CurrentUser):
    svc = OTPService()
    try:
        ttl = await svc.send(str(current_user.id), body.phone)
    except ValueError as e:
        raise ValidationError(str(e))
    return OTPSendResponse(expires_in=ttl)


@router.post("/verify", response_model=OTPVerifyResponse)
async def verify_otp(
    body: OTPVerifyRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    svc = OTPService()
    try:
        verified = await svc.verify(str(current_user.id), body.code)
    except ValueError as e:
        raise ValidationError(str(e))
    if verified:
        repo = UserRepository(session)
        await repo.update(current_user.id, phone=body.phone, is_verified=True)
    return OTPVerifyResponse(verified=verified)
