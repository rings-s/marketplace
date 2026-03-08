import structlog
import httpx
from app.config import settings

logger = structlog.get_logger()
OURSMS_BASE_URL = "https://oursms.app/api/v1"


class OurSMSClient:
    def __init__(self) -> None:
        self._auth = httpx.BasicAuth(settings.OURSMS_APP_SID, settings.OURSMS_APP_SECRET)

    async def send_message(self, *, phone: str, body: str) -> dict:
        payload = {
            "AppSid": settings.OURSMS_APP_SID,
            "Body": body,
            "Recipients": [phone],
            "SenderID": settings.OURSMS_SENDER_ID,
            "responseType": "json",
            "CorrelationID": "",
        }
        async with httpx.AsyncClient(auth=self._auth, timeout=15) as client:
            resp = await client.post(f"{OURSMS_BASE_URL}/msgs", json=payload)
            resp.raise_for_status()
            return resp.json()


class SMSService:
    def __init__(self, client: OurSMSClient | None = None) -> None:
        self._client = client or OurSMSClient()

    async def send_otp(self, phone: str, code: str) -> None:
        if not settings.OURSMS_APP_SID:
            logger.warning("oursms_not_configured", phone=phone)
            return
        try:
            result = await self._client.send_message(
                phone=phone,
                body=f"رمز التحقق الخاص بك هو: {code}",
            )
            logger.info("sms_sent", phone=phone, operation_id=result.get("OperationID"))
        except httpx.HTTPStatusError as exc:
            logger.error("sms_send_failed", phone=phone, status=exc.response.status_code)
            raise
