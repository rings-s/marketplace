import re
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_google_token, create_access_token, create_refresh_token
from app.repositories.user import UserRepository
from app.models.user import User


def _generate_username(name: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]", "", name.lower())[:20] or "user"
    return f"{base}_{uuid.uuid4().hex[:6]}"


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def google_login(self, id_token_str: str) -> tuple[User, str, str]:
        """Verify Google token, upsert user, return (user, access_token, refresh_token)."""
        claims = verify_google_token(id_token_str)
        google_sub = claims["sub"]
        email = claims.get("email", "")
        full_name = claims.get("name", "")
        avatar_url = claims.get("picture")

        user = await self.repo.get_by_google_sub(google_sub)
        if not user:
            user = await self.repo.get_by_email(email)
            if user:
                # Link Google account to existing email user
                await self.repo.update(
                    user.id,
                    google_sub=google_sub,
                    avatar_url=avatar_url or user.avatar_url,
                )
                user = await self.repo.get(user.id)
            else:
                user = await self.repo.create(
                    google_sub=google_sub,
                    email=email,
                    full_name=full_name,
                    username=_generate_username(full_name),
                    avatar_url=avatar_url,
                    is_verified=True,
                )

        access = create_access_token(str(user.id), {"role": user.role})
        refresh = create_refresh_token(str(user.id))
        return user, access, refresh
