import re
from pydantic import BaseModel, field_validator

KSA_PHONE_RE = re.compile(r"^\+9665\d{8}$")


class OTPSendRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not KSA_PHONE_RE.match(v):
            raise ValueError("Must be a valid Saudi mobile number (+9665XXXXXXXX)")
        return v


class OTPSendResponse(BaseModel):
    expires_in: int = 300


class OTPVerifyRequest(BaseModel):
    phone: str
    code: str

    @field_validator("code")
    @classmethod
    def code_format(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("OTP must be 6 digits")
        return v


class OTPVerifyResponse(BaseModel):
    verified: bool
