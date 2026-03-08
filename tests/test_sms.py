import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.sms import OurSMSClient, SMSService


@pytest.mark.asyncio
async def test_oursms_client_send_message():
    mock_response = MagicMock()
    mock_response.json.return_value = {"OperationID": "abc123", "Status": "Sent"}
    mock_response.raise_for_status = MagicMock()

    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=False)

    with patch("app.services.sms.httpx.AsyncClient", return_value=mock_client_instance):
        client = OurSMSClient()
        result = await client.send_message(phone="+966512345678", body="Test message")

    assert result["OperationID"] == "abc123"
    mock_client_instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_sms_service_send_otp_success():
    mock_client = AsyncMock(spec=OurSMSClient)
    mock_client.send_message.return_value = {"OperationID": "xyz789"}

    with patch("app.services.sms.settings") as mock_settings:
        mock_settings.OURSMS_APP_SID = "test-sid"
        mock_settings.OURSMS_APP_SECRET = "test-secret"
        mock_settings.OURSMS_SENDER_ID = "Marketplace"

        svc = SMSService(client=mock_client)
        await svc.send_otp("+966512345678", "123456")

    mock_client.send_message.assert_called_once_with(
        phone="+966512345678",
        body="رمز التحقق الخاص بك هو: 123456",
    )


@pytest.mark.asyncio
async def test_sms_service_skips_when_not_configured():
    mock_client = AsyncMock(spec=OurSMSClient)

    with patch("app.services.sms.settings") as mock_settings:
        mock_settings.OURSMS_APP_SID = ""

        svc = SMSService(client=mock_client)
        await svc.send_otp("+966512345678", "123456")

    mock_client.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_sms_service_raises_on_http_error():
    import httpx

    mock_client = AsyncMock(spec=OurSMSClient)
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_client.send_message.side_effect = httpx.HTTPStatusError(
        "Unauthorized", request=MagicMock(), response=mock_response
    )

    with patch("app.services.sms.settings") as mock_settings:
        mock_settings.OURSMS_APP_SID = "test-sid"
        mock_settings.OURSMS_APP_SECRET = "test-secret"
        mock_settings.OURSMS_SENDER_ID = "Marketplace"

        svc = SMSService(client=mock_client)
        with pytest.raises(httpx.HTTPStatusError):
            await svc.send_otp("+966512345678", "123456")
