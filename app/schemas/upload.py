from pydantic import BaseModel, field_validator


class PresignedRequest(BaseModel):
    count: int
    item_id: str | None = None

    @field_validator("count")
    @classmethod
    def count_range(cls, v: int) -> int:
        if not 1 <= v <= 10:
            raise ValueError("count must be between 1 and 10")
        return v


class PresignedURLItem(BaseModel):
    upload_url: str
    key: str
    photo_index: int


class ConfirmUploadRequest(BaseModel):
    keys: list[str]

    @field_validator("keys")
    @classmethod
    def keys_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("keys must not be empty")
        if len(v) > 10:
            raise ValueError("max 10 keys")
        return v


class ConfirmedPhoto(BaseModel):
    key: str
    url: str
