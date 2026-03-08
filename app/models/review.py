from __future__ import annotations
import uuid
from sqlalchemy import ForeignKey, Integer, Text, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.models.base import UUIDMixin, TimestampMixin
from app.database import Base


class Review(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "reviews"
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating"),)

    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), unique=True, nullable=False)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    reviewee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)

    reviewer: Mapped[User] = relationship("User", foreign_keys=[reviewer_id])
    reviewee: Mapped[User] = relationship("User", foreign_keys=[reviewee_id])
