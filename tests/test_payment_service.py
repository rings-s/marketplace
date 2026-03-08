import os
import pytest
from decimal import Decimal
from app.services.payment import _calculate_fees, _to_halalas, PaymentService


def test_fee_calculation_1_percent():
    fee, seller = _calculate_fees(Decimal("1000.00"))
    assert fee == Decimal("10.00")
    assert seller == Decimal("990.00")


def test_fee_calculation_rounds():
    fee, seller = _calculate_fees(Decimal("99.99"))
    assert fee == Decimal("1.00")
    assert seller == Decimal("98.99")


def test_to_halalas():
    assert _to_halalas(Decimal("100.00")) == 10000
    assert _to_halalas(Decimal("1.50")) == 150


def test_webhook_secret_verify_correct():
    from unittest.mock import patch
    with patch("app.services.payment.settings") as mock_settings:
        mock_settings.MOYASAR_WEBHOOK_SECRET = "test-secret"
        result = PaymentService.verify_webhook_secret({"secret_token": "test-secret"})
    assert result is True


def test_webhook_secret_verify_wrong():
    from unittest.mock import patch
    with patch("app.services.payment.settings") as mock_settings:
        mock_settings.MOYASAR_WEBHOOK_SECRET = "test-secret"
        result = PaymentService.verify_webhook_secret({"secret_token": "wrong"})
    assert result is False
