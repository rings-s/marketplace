import json
import secrets
import structlog
import redis.asyncio as aioredis
from app.config import settings
from app.services.sms import SMSService

logger = structlog.get_logger()

OTP_TTL = 300        # 5 minutes
RATE_LIMIT_TTL = 60  # 1 per minute
MAX_ATTEMPTS = 3


class OTPService:
    def __init__(self) -> None:
        self._redis: aioredis.Redis | None = None

    async def _get_redis(self) -> aioredis.Redis:
        if not self._redis:
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._redis

    def _otp_key(self, user_id: str) -> str:
        return f"otp:{user_id}"

    def _rate_key(self, user_id: str) -> str:
        return f"otp_sent:{user_id}"

    async def send(self, user_id: str, phone: str) -> int:
        """Generate and store OTP. Returns TTL. Raises if rate-limited."""
        r = await self._get_redis()
        if await r.exists(self._rate_key(user_id)):
            raise ValueError("OTP already sent recently. Please wait 60 seconds.")
        code = f"{secrets.randbelow(1_000_000):06d}"
        payload = json.dumps({"code": code, "attempts": 0})
        await r.setex(self._otp_key(user_id), OTP_TTL, payload)
        await r.setex(self._rate_key(user_id), RATE_LIMIT_TTL, "1")
        sms = SMSService()
        try:
            await sms.send_otp(phone, code)
        except Exception:
            logger.warning("sms_delivery_failed", user_id=user_id)
        logger.info("otp_generated", user_id=user_id)
        return OTP_TTL

    async def verify(self, user_id: str, code: str) -> bool:
        """Verify OTP. Returns True on success. Raises on max attempts or expired."""
        r = await self._get_redis()
        raw = await r.get(self._otp_key(user_id))
        if not raw:
            raise ValueError("OTP expired or not found. Please request a new one.")
        payload = json.loads(raw)
        attempts = payload["attempts"] + 1
        if payload["code"] != code:
            if attempts >= MAX_ATTEMPTS:
                await r.delete(self._otp_key(user_id))
                raise ValueError("Too many failed attempts. Please request a new OTP.")
            payload["attempts"] = attempts
            await r.setex(self._otp_key(user_id), OTP_TTL, json.dumps(payload))
            return False
        await r.delete(self._otp_key(user_id))
        return True
