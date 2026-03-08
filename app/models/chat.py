from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Boolean, DateTime, Enum as SAEnum, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.models.base import UUIDMixin, TimestampMixin
from app.core.enums import ContentType
from app.database import Base


class ChatThread(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "chat_threads"

    item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("furniture_items.id"))
    buyer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    seller_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    item: Mapped["FurnitureItem | None"] = relationship("FurnitureItem")
    buyer: Mapped["User"] = relationship("User", foreign_keys=[buyer_id])
    seller: Mapped["User"] = relationship("User", foreign_keys=[seller_id])
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="thread",
        order_by="ChatMessage.sent_at",
    )


class ChatMessage(UUIDMixin, Base):
    __tablename__ = "chat_messages"

    thread_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chat_threads.id"), nullable=False, index=True
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    content_text: Mapped[str | None] = mapped_column(Text)
    content_type: Mapped[ContentType] = mapped_column(
        SAEnum(ContentType), default=ContentType.text, nullable=False
    )
    media_url: Mapped[str | None] = mapped_column(String(2048))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    thread: Mapped[ChatThread] = relationship("ChatThread", back_populates="messages")
    sender: Mapped["User"] = relationship("User", back_populates="sent_messages")
