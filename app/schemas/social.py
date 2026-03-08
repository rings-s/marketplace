from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.core.enums import ReportTargetType, ReportStatus, OrderStatus


class FavoriteResponse(BaseModel):
    user_id: UUID
    item_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportCreate(BaseModel):
    target_type: ReportTargetType
    target_id: UUID
    reason: str


class ReportResponse(BaseModel):
    id: UUID
    reporter_id: UUID
    target_type: ReportTargetType
    target_id: UUID
    reason: str
    status: ReportStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    item_id: UUID
    inquiry_message: str | None = None


class OrderResponse(BaseModel):
    id: UUID
    item_id: UUID
    buyer_id: UUID
    seller_id: UUID
    status: OrderStatus
    inquiry_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
