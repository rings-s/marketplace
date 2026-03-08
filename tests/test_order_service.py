import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from uuid import uuid4
from app.services.order import OrderService
from app.models.offer import OfferStatus
from app.core.enums import OrderStatus
from app.core.exceptions import ForbiddenError, ConflictError


@pytest.mark.asyncio
async def test_accept_own_offer_raises():
    session = AsyncMock()
    svc = OrderService(session)
    buyer_id = uuid4()
    offer_id = uuid4()
    order_id = uuid4()

    mock_offer = MagicMock()
    mock_offer.id = offer_id
    mock_offer.order_id = order_id
    mock_offer.offered_by = buyer_id
    mock_offer.status = OfferStatus.pending
    mock_offer.amount_sar = Decimal("500")

    mock_order = MagicMock()
    mock_order.buyer_id = buyer_id
    mock_order.seller_id = uuid4()

    svc.offer_repo = AsyncMock()
    svc.offer_repo.get_or_404 = AsyncMock(return_value=mock_offer)
    svc.order_repo = AsyncMock()
    svc.order_repo.get_or_404 = AsyncMock(return_value=mock_order)

    with pytest.raises(ForbiddenError):
        await svc.accept_offer(offer_id=offer_id, user_id=buyer_id)


@pytest.mark.asyncio
async def test_cancel_completed_order_raises():
    session = AsyncMock()
    svc = OrderService(session)
    user_id = uuid4()
    order_id = uuid4()

    mock_order = MagicMock()
    mock_order.buyer_id = user_id
    mock_order.seller_id = uuid4()
    mock_order.status = OrderStatus.completed

    svc.order_repo = AsyncMock()
    svc.order_repo.get_or_404 = AsyncMock(return_value=mock_order)
    svc.offer_repo = AsyncMock()

    with pytest.raises(ConflictError):
        await svc.cancel_order(order_id=order_id, user_id=user_id)
