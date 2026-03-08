from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import CurrentUser
from app.schemas.payment import CheckoutRequest, PaymentResponse
from app.services.payment import PaymentService
from app.core.exceptions import ForbiddenError, PaymentError
from app.repositories.payment import PaymentRepository
from app.repositories.social import OrderRepository

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/checkout", response_model=PaymentResponse, status_code=201)
async def checkout(
    body: CheckoutRequest,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    order_repo = OrderRepository(session)
    order = await order_repo.get_or_404(body.order_id)
    if order.buyer_id != current_user.id:
        raise ForbiddenError("Not your order")

    service = PaymentService(session)
    payment = await service.initiate_checkout(
        order_id=body.order_id,
        amount_sar=order.item.price_sar if hasattr(order, "item") else body.source.get("amount"),
        source=body.source,
        callback_url=body.callback_url,
    )
    return payment


@router.get("/callback", response_model=PaymentResponse)
async def payment_callback(
    payment_id: str,
    order_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    service = PaymentService(session)
    return await service.verify_callback(payment_id, order_id)


@router.post("/webhook")
async def moyasar_webhook(request: Request, session: AsyncSession = Depends(get_db)):
    """Idempotent Moyasar webhook handler."""
    payload = await request.json()

    if not PaymentService.verify_webhook_secret(payload):
        raise PaymentError("Invalid webhook secret")

    service = PaymentService(session)
    await service.handle_webhook(payload)
    # Always return 200 quickly
    return {"received": True}


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = PaymentRepository(session)
    return await repo.get_or_404(payment_id)
