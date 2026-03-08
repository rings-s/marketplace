from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Any
from app.core.enums import ItemCondition, ItemStatus, SellerType


class ItemCreate(BaseModel):
    title_ar: str
    title_en: str
    description_ar: str | None = None
    description_en: str | None = None
    price_sar: Decimal
    condition: ItemCondition
    category_main: str
    photos: list[str] = []
    location_city: str
    lat: float | None = None
    lon: float | None = None
    seller_type: SellerType
    tag_ids: list[UUID] = []

    @field_validator("price_sar")
    @classmethod
    def price_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


class ItemUpdate(BaseModel):
    title_ar: str | None = None
    title_en: str | None = None
    description_ar: str | None = None
    description_en: str | None = None
    price_sar: Decimal | None = None
    condition: ItemCondition | None = None
    photos: list[str] | None = None
    location_city: str | None = None
    lat: float | None = None
    lon: float | None = None
    status: ItemStatus | None = None
    tag_ids: list[UUID] | None = None

    @field_validator("price_sar")
    @classmethod
    def price_must_be_positive(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


class TagResponse(BaseModel):
    id: UUID
    name_ar: str
    name_en: str
    slug: str
    category: str | None

    model_config = {"from_attributes": True}


class ItemResponse(BaseModel):
    id: UUID
    title_ar: str
    title_en: str
    description_ar: str | None
    description_en: str | None
    price_sar: Decimal
    condition: ItemCondition
    category_main: str
    photos: list[Any]
    location_city: str
    lat: float | None
    lon: float | None
    seller_type: SellerType
    individual_seller_id: UUID | None
    store_id: UUID | None
    status: ItemStatus
    views_count: int
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class ItemListResponse(BaseModel):
    items: list[ItemResponse]
    total: int
    page: int
    size: int
    pages: int


class CursorItemListResponse(BaseModel):
    items: list[ItemResponse]
    next_cursor: str | None
    has_more: bool
    total: int
