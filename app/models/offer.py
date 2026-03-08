from __future__ import annotations
import uuid
import enum
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, Text, Enum as SAEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.models.base import UUIDMixin, TimestampMixin
from app.database import Base


class OfferStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    countered = "countered"
    superseded = "superseded"


class PriceOffer(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "price_offers"

    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)
    offered_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    amount_sar: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    status: Mapped[OfferStatus] = mapped_column(
        SAEnum(OfferStatus), default=OfferStatus.pending, nullable=False
    )

    order: Mapped[Order] = relationship("Order")
    offerer: Mapped[User] = relationship("User", foreign_keys=[offered_by])
