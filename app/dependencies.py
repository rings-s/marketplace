from typing import Annotated
from fastapi import Depends, Cookie, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.repositories.user import UserRepository
from app.models.user import User
from app.core.enums import UserRole


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    access_token: Annotated[str | None, Cookie()] = None,
    session: AsyncSession = Depends(get_db),
) -> User:
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    elif access_token:
        token = access_token

    if not token:
        raise UnauthorizedError()

    payload = decode_token(token, "access")
    user_id = payload.get("sub")
    repo = UserRepository(session)
    user = await repo.get(user_id)
    if not user or not user.is_active:
        raise UnauthorizedError()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    async def _check(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise ForbiddenError("Insufficient permissions")
        return current_user
    return _check
