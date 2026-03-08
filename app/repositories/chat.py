from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import ChatThread, ChatMessage
from app.core.enums import ContentType
from app.repositories.base import BaseRepository


class ChatRepository(BaseRepository[ChatThread]):
    def __init__(self, session: AsyncSession):
        super().__init__(ChatThread, session)

    async def get_thread(self, thread_id: UUID | str) -> ChatThread | None:
        return await self.get(thread_id)

    async def get_thread_by_participants(
        self, buyer_id: UUID, seller_id: UUID, item_id: UUID | None = None
    ) -> ChatThread | None:
        stmt = select(ChatThread).where(
            and_(ChatThread.buyer_id == buyer_id, ChatThread.seller_id == seller_id)
        )
        if item_id:
            stmt = stmt.where(ChatThread.item_id == item_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_threads_for_user(self, user_id: UUID) -> list[ChatThread]:
        stmt = (
            select(ChatThread)
            .where(
                (ChatThread.buyer_id == user_id) | (ChatThread.seller_id == user_id)
            )
            .order_by(ChatThread.last_message_at.desc().nullslast())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_messages_by_thread(
        self, thread_id: UUID, offset: int = 0, limit: int = 50
    ) -> list[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.sent_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_message(
        self,
        *,
        thread_id: UUID | str,
        sender_id: UUID | str,
        content_text: str | None,
        content_type: str = "text",
        sent_at: datetime | None = None,
        media_url: str | None = None,
    ) -> ChatMessage:
        if sent_at is None:
            sent_at = datetime.now(timezone.utc)
        msg = ChatMessage(
            thread_id=thread_id,
            sender_id=sender_id,
            content_text=content_text,
            content_type=ContentType(content_type),
            sent_at=sent_at,
            media_url=media_url,
        )
        self.session.add(msg)
        # update thread's last_message_at
        await self.session.execute(
            update(ChatThread)
            .where(ChatThread.id == thread_id)
            .values(last_message_at=sent_at)
        )
        await self.session.flush()
        await self.session.refresh(msg)
        return msg

    async def mark_messages_read(self, thread_id: UUID | str, user_id: UUID | str) -> None:
        await self.session.execute(
            update(ChatMessage)
            .where(
                and_(
                    ChatMessage.thread_id == thread_id,
                    ChatMessage.sender_id != user_id,
                    ChatMessage.is_read.is_(False),
                )
            )
            .values(is_read=True)
        )
        await self.session.flush()
