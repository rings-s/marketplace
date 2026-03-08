from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.models.offer import OfferStatus


class OfferCreate(BaseModel):
    amount_sar: Decimal
    message: str | None = None

    @field_validator("amount_sar")
    @classmethod
    def positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class OfferResponse(BaseModel):
    id: UUID
    order_id: UUID
    offered_by: UUID
    amount_sar: Decimal
    message: str | None
    status: OfferStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderDetailResponse(BaseModel):
    id: UUID
    item_id: UUID
    buyer_id: UUID
    seller_id: UUID
    status: str
    inquiry_message: str | None
    created_at: datetime
    latest_offer: OfferResponse | None = None

    model_config = {"from_attributes": True}
