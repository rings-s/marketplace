import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, ForeignKey, Numeric, Float, Integer, Enum as SAEnum, Text, JSON, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.models.base import UUIDMixin, TimestampMixin
from app.core.enums import ItemCondition, ItemStatus, SellerType
from app.database import Base


class Tag(UUIDMixin, Base):
    __tablename__ = "tags"

    name_ar: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))

    items: Mapped[list["FurnitureItemTag"]] = relationship("FurnitureItemTag", back_populates="tag")


class FurnitureItemTag(Base):
    __tablename__ = "furniture_item_tags"

    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("furniture_items.id"), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id"), primary_key=True)

    item: Mapped["FurnitureItem"] = relationship("FurnitureItem", back_populates="item_tags")
    tag: Mapped[Tag] = relationship("Tag", back_populates="items")


class FurnitureItem(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "furniture_items"

    title_ar: Mapped[str] = mapped_column(String(500), nullable=False)
    title_en: Mapped[str] = mapped_column(String(500), nullable=False)
    description_ar: Mapped[str | None] = mapped_column(Text)
    description_en: Mapped[str | None] = mapped_column(Text)
    price_sar: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    condition: Mapped[ItemCondition] = mapped_column(SAEnum(ItemCondition), nullable=False)
    category_main: Mapped[str] = mapped_column(String(100), nullable=False)
    photos: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    location_city: Mapped[str] = mapped_column(String(100), nullable=False)
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    seller_type: Mapped[SellerType] = mapped_column(SAEnum(SellerType), nullable=False)
    individual_seller_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    store_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("stores.id"))
    status: Mapped[ItemStatus] = mapped_column(
        SAEnum(ItemStatus), default=ItemStatus.active, nullable=False
    )
    views_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    individual_seller: Mapped["User | None"] = relationship(
        "User", foreign_keys=[individual_seller_id]
    )
    store: Mapped["Store | None"] = relationship("Store", back_populates="items")
    item_tags: Mapped[list[FurnitureItemTag]] = relationship(
        "FurnitureItemTag", back_populates="item", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["Favorite"]] = relationship("Favorite", back_populates="item")
