import re
from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from datetime import datetime
from app.core.enums import UserRole

KSA_PHONE_RE = re.compile(r"^\+9665\d{8}$")


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    username: str
    phone: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_ksa_phone(cls, v: str | None) -> str | None:
        if v and not KSA_PHONE_RE.match(v):
            raise ValueError("Phone must be a valid Saudi mobile number (+9665XXXXXXXX)")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]{3,30}$", v):
            raise ValueError("Username must be 3-30 alphanumeric chars or underscores")
        return v


class UserUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    city: str | None = None
    avatar_url: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_ksa_phone(cls, v: str | None) -> str | None:
        if v and not KSA_PHONE_RE.match(v):
            raise ValueError("Phone must be a valid Saudi mobile number")
        return v


class UserResponse(BaseModel):
    id: UUID
    email: str
    phone: str | None
    full_name: str
    username: str
    avatar_url: str | None
    role: UserRole
    city: str | None
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}
