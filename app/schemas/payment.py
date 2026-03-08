from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Any
from app.core.enums import PaymentStatus


class CheckoutRequest(BaseModel):
    order_id: UUID
    source: dict[str, Any]  # creditcard / stcpay / applepay details
    callback_url: str


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    moyasar_payment_id: str | None
    amount_sar: Decimal
    platform_fee_sar: Decimal
    seller_amount_sar: Decimal
    status: PaymentStatus
    payment_method: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MoyasarWebhookPayload(BaseModel):
    id: str
    type: str
    secret_token: str
    data: dict[str, Any]
