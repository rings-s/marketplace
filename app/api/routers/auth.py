from fastapi import APIRouter, Depends, Response, Cookie
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import GoogleAuthRequest, TokenResponse
from app.services.auth import AuthService
from app.config import settings
from app.core.security import decode_token, create_access_token, create_refresh_token
from app.core.exceptions import UnauthorizedError
from app.repositories.user import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google", response_model=TokenResponse)
async def google_login(
    body: GoogleAuthRequest,
    response: Response,
    session: AsyncSession = Depends(get_db),
):
    service = AuthService(session)
    user, access, refresh = await service.google_login(body.id_token)

    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=settings.is_production,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )
    return TokenResponse(
        access_token=access,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    session: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise UnauthorizedError("No refresh token")
    payload = decode_token(refresh_token, "refresh")
    repo = UserRepository(session)
    user = await repo.get(payload["sub"])
    if not user or not user.is_active:
        raise UnauthorizedError()
    access = create_access_token(str(user.id), {"role": user.role})
    new_refresh = create_refresh_token(str(user.id))
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=settings.is_production,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )
    return TokenResponse(
        access_token=access,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}
