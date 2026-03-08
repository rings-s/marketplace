from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime


class ReviewCreate(BaseModel):
    order_id: UUID
    rating: int
    comment: str | None = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewResponse(BaseModel):
    id: UUID
    order_id: UUID
    reviewer_id: UUID
    reviewee_id: UUID
    rating: int
    comment: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
