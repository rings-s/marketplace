from pydantic import BaseModel, field_validator


class DeviceTokenCreate(BaseModel):
    token: str

    @field_validator("token")
    @classmethod
    def valid_expo_token(cls, v: str) -> str:
        if not (v.startswith("ExponentPushToken[") or v.startswith("ExpoPushToken[")):
            raise ValueError("Must be a valid Expo push token")
        return v


class DeviceTokenResponse(BaseModel):
    registered: bool
