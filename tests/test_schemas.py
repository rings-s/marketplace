import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate


def test_valid_ksa_phone():
    u = UserCreate(email="a@b.com", full_name="Ahmed", username="ahmed1", phone="+966512345678")
    assert u.phone == "+966512345678"


def test_invalid_phone_raises():
    with pytest.raises(ValidationError):
        UserCreate(email="a@b.com", full_name="Ahmed", username="ahmed1", phone="0512345678")


def test_invalid_username_raises():
    with pytest.raises(ValidationError):
        UserCreate(email="a@b.com", full_name="Ahmed", username="a b")
