import uuid
from decimal import Decimal
from sqlalchemy import String, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.models.base import UUIDMixin, TimestampMixin
from app.database import Base


class Store(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "stores"

    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    commercial_register_number: Mapped[str | None] = mapped_column(String(50))
    store_name: Mapped[str] = mapped_column(String(255), nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(2048))
    description: Mapped[str | None] = mapped_column(Text)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avg_rating: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), default=Decimal("0.00"), nullable=False
    )

    owner: Mapped["User"] = relationship("User", back_populates="store")
    items: Mapped[list["FurnitureItem"]] = relationship("FurnitureItem", back_populates="store")
