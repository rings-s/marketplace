import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, ForeignKey, Numeric, JSON, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.models.base import UUIDMixin, TimestampMixin
from app.core.enums import PaymentStatus
from app.database import Base


class Payment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "payments"

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id"), unique=True, nullable=False
    )
    moyasar_payment_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True
    )
    amount_sar: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    platform_fee_sar: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    seller_amount_sar: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus), default=PaymentStatus.initiated, nullable=False
    )
    payment_method: Mapped[str | None] = mapped_column(String(50))
    given_id: Mapped[uuid.UUID] = mapped_column(unique=True, default=uuid.uuid4, nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="payment")


class WebhookEvent(Base):
    """Idempotency store for Moyasar webhook events."""
    __tablename__ = "webhook_events"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
