from __future__ import annotations
import uuid
import enum
from sqlalchemy import String, Boolean, ForeignKey, Enum as SAEnum, JSON, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.models.base import UUIDMixin, TimestampMixin
from app.database import Base


class NotificationType(str, enum.Enum):
    new_message = "new_message"
    offer_received = "offer_received"
    offer_accepted = "offer_accepted"
    offer_rejected = "offer_rejected"
    order_update = "order_update"
    review_received = "review_received"


class Notification(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    type: Mapped[NotificationType] = mapped_column(SAEnum(NotificationType), nullable=False)
    title_ar: Mapped[str] = mapped_column(String(255), nullable=False)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)
    body_ar: Mapped[str] = mapped_column(Text, nullable=False)
    body_en: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User] = relationship("User")
