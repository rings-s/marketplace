import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Enum as SAEnum, Text, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.models.base import UUIDMixin, TimestampMixin
from app.core.enums import ReportTargetType, ReportStatus, OrderStatus
from app.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("furniture_items.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="favorites")
    item: Mapped["FurnitureItem"] = relationship("FurnitureItem", back_populates="favorites")


class Report(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "reports"

    reporter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    target_type: Mapped[ReportTargetType] = mapped_column(SAEnum(ReportTargetType), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        SAEnum(ReportStatus), default=ReportStatus.pending, nullable=False
    )

    reporter: Mapped["User"] = relationship(
        "User", back_populates="reports", foreign_keys=[reporter_id]
    )


class Order(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "orders"

    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("furniture_items.id"), nullable=False)
    buyer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    seller_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus), default=OrderStatus.inquiry, nullable=False
    )
    inquiry_message: Mapped[str | None] = mapped_column(Text)

    item: Mapped["FurnitureItem"] = relationship("FurnitureItem")
    buyer: Mapped["User"] = relationship("User", foreign_keys=[buyer_id])
    seller: Mapped["User"] = relationship("User", foreign_keys=[seller_id])
    payment: Mapped["Payment | None"] = relationship(
        "Payment", back_populates="order", uselist=False
    )
