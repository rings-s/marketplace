import hmac
import uuid
from decimal import Decimal, ROUND_HALF_UP
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.core.enums import PaymentStatus
from app.core.exceptions import PaymentError
from app.repositories.payment import PaymentRepository
from app.models.payment import Payment

PLATFORM_FEE = Decimal(str(settings.PLATFORM_FEE_PERCENT)) / Decimal("100")


def _calculate_fees(amount_sar: Decimal) -> tuple[Decimal, Decimal]:
    """Returns (platform_fee_sar, seller_amount_sar). Rounds to 2dp."""
    fee = (amount_sar * PLATFORM_FEE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    seller = amount_sar - fee
    return fee, seller


def _to_halalas(amount_sar: Decimal) -> int:
    """Convert SAR to halalas (× 100) as integer for Moyasar API."""
    return int((amount_sar * 100).quantize(Decimal("1")))


class MoyasarClient:
    """Thin async wrapper around Moyasar REST API."""

    def __init__(self) -> None:
        self._auth = httpx.BasicAuth(settings.MOYASAR_SECRET_KEY, "")
        self._base = settings.MOYASAR_BASE_URL

    async def create_payment(
        self,
        *,
        amount_sar: Decimal,
        description: str,
        callback_url: str,
        source: dict,
        given_id: uuid.UUID,
        metadata: dict | None = None,
    ) -> dict:
        async with httpx.AsyncClient(auth=self._auth, timeout=30) as client:
            resp = await client.post(
                f"{self._base}/payments",
                json={
                    "amount": _to_halalas(amount_sar),
                    "currency": "SAR",
                    "description": description,
                    "callback_url": callback_url,
                    "source": source,
                    "given_id": str(given_id),
                    "metadata": metadata or {},
                },
            )
            if resp.status_code not in (200, 201):
                raise PaymentError(
                    f"Moyasar error: {resp.json().get('message', 'unknown')}"
                )
            return resp.json()

    async def get_payment(self, payment_id: str) -> dict:
        async with httpx.AsyncClient(auth=self._auth, timeout=30) as client:
            resp = await client.get(f"{self._base}/payments/{payment_id}")
            if resp.status_code != 200:
                raise PaymentError("Payment not found on Moyasar")
            return resp.json()

    async def refund_payment(
        self, payment_id: str, amount_sar: Decimal | None = None
    ) -> dict:
        body: dict = {}
        if amount_sar is not None:
            body["amount"] = _to_halalas(amount_sar)
        async with httpx.AsyncClient(auth=self._auth, timeout=30) as client:
            resp = await client.post(
                f"{self._base}/payments/{payment_id}/refund", json=body
            )
            if resp.status_code != 200:
                raise PaymentError("Refund failed")
            return resp.json()


class PaymentService:
    def __init__(
        self, session: AsyncSession, moyasar: MoyasarClient | None = None
    ) -> None:
        self.session = session
        self.repo = PaymentRepository(session)
        self.moyasar = moyasar or MoyasarClient()

    async def initiate_checkout(
        self,
        order_id: uuid.UUID,
        amount_sar: Decimal,
        source: dict,
        callback_url: str,
    ) -> Payment:
        fee, seller_amount = _calculate_fees(amount_sar)
        given_id = uuid.uuid4()

        data = await self.moyasar.create_payment(
            amount_sar=amount_sar,
            description=f"Marketplace order {order_id}",
            callback_url=callback_url,
            source=source,
            given_id=given_id,
            metadata={"order_id": str(order_id)},
        )

        payment = await self.repo.create(
            order_id=order_id,
            moyasar_payment_id=data["id"],
            amount_sar=amount_sar,
            platform_fee_sar=fee,
            seller_amount_sar=seller_amount,
            status=PaymentStatus.initiated,
            payment_method=source.get("type"),
            given_id=given_id,
            metadata_=data,
        )
        return payment

    async def verify_callback(
        self, moyasar_payment_id: str, expected_order_id: uuid.UUID
    ) -> Payment:
        """Called after 3DS redirect. Verifies amount + status server-side."""
        data = await self.moyasar.get_payment(moyasar_payment_id)

        payment = await self.repo.get_by_moyasar_id(moyasar_payment_id)
        if not payment:
            raise PaymentError("Payment not found locally")
        if str(payment.order_id) != str(expected_order_id):
            raise PaymentError("Order mismatch")
        if data["currency"] != "SAR":
            raise PaymentError("Currency mismatch")
        if data["amount"] != _to_halalas(payment.amount_sar):
            raise PaymentError("Amount mismatch — possible tampering")

        status_str = data.get("status", "")
        new_status = (
            PaymentStatus(status_str)
            if status_str in PaymentStatus.__members__
            else PaymentStatus.failed
        )
        await self.repo.update(payment.id, status=new_status, metadata_=data)
        return payment

    async def handle_webhook(self, payload: dict) -> bool:
        """Idempotent webhook handler. Returns True if processed, False if duplicate."""
        event_id = payload.get("id")
        if not event_id:
            return False

        existing = await self.repo.get_webhook_event(event_id)
        if existing:
            return False  # already processed

        await self.repo.create_webhook_event(
            event_id=event_id, event_type=payload.get("type", "")
        )

        payment_data = payload.get("data", {})
        moyasar_id = payment_data.get("id")
        if moyasar_id:
            payment = await self.repo.get_by_moyasar_id(moyasar_id)
            if payment:
                status_str = payment_data.get("status", "")
                if status_str in PaymentStatus.__members__:
                    await self.repo.update(payment.id, status=PaymentStatus(status_str))
        return True

    @staticmethod
    def verify_webhook_secret(payload: dict) -> bool:
        """Constant-time comparison of webhook secret_token."""
        incoming = payload.get("secret_token", "")
        return hmac.compare_digest(
            incoming.encode(), settings.MOYASAR_WEBHOOK_SECRET.encode()
        )
