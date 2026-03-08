from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class StoreCreate(BaseModel):
    store_name: str
    commercial_register_number: str | None = None
    description: str | None = None


class StoreUpdate(BaseModel):
    store_name: str | None = None
    commercial_register_number: str | None = None
    description: str | None = None
    logo_url: str | None = None


class StoreResponse(BaseModel):
    id: UUID
    owner_user_id: UUID
    store_name: str
    commercial_register_number: str | None
    logo_url: str | None
    description: str | None
    verified: bool
    avg_rating: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}
