from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import CurrentUser
from app.schemas.offer import OfferCreate, OfferResponse
from app.schemas.social import OrderCreate, OrderResponse
from app.services.order import OrderService
from app.repositories.order import OrderRepository
from app.repositories.item import ItemRepository
from app.core.exceptions import ForbiddenError

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    body: OrderCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    item_repo = ItemRepository(session)
    item = await item_repo.get_or_404(body.item_id)
    seller_id = item.individual_seller_id or (
        item.store.owner_user_id if item.store else None
    )
    svc = OrderService(session)
    return await svc.create_order(
        item_id=body.item_id,
        buyer_id=current_user.id,
        seller_id=seller_id,
        inquiry_message=body.inquiry_message,
    )


@router.get("", response_model=list[OrderResponse])
async def list_orders(current_user: CurrentUser, session: AsyncSession = Depends(get_db)):
    repo = OrderRepository(session)
    return await repo.list_for_user(current_user.id)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID, current_user: CurrentUser, session: AsyncSession = Depends(get_db)
):
    repo = OrderRepository(session)
    order = await repo.get_or_404(order_id)
    if current_user.id not in (order.buyer_id, order.seller_id):
        raise ForbiddenError()
    return order


@router.post("/{order_id}/offers", response_model=OfferResponse, status_code=201)
async def make_offer(
    order_id: UUID,
    body: OfferCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    svc = OrderService(session)
    return await svc.make_offer(
        order_id=order_id,
        offered_by=current_user.id,
        amount_sar=body.amount_sar,
        message=body.message,
    )


@router.post("/{order_id}/offers/{offer_id}/accept", response_model=OfferResponse)
async def accept_offer(
    order_id: UUID,
    offer_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    svc = OrderService(session)
    return await svc.accept_offer(offer_id=offer_id, user_id=current_user.id)


@router.post("/{order_id}/offers/{offer_id}/reject", response_model=OfferResponse)
async def reject_offer(
    order_id: UUID,
    offer_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    svc = OrderService(session)
    return await svc.reject_offer(offer_id=offer_id, user_id=current_user.id)


@router.post("/{order_id}/offers/{offer_id}/counter", response_model=OfferResponse, status_code=201)
async def counter_offer(
    order_id: UUID,
    offer_id: UUID,
    body: OfferCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    svc = OrderService(session)
    return await svc.counter_offer(
        offer_id=offer_id,
        user_id=current_user.id,
        amount_sar=body.amount_sar,
        message=body.message,
    )


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: UUID, current_user: CurrentUser, session: AsyncSession = Depends(get_db)
):
    svc = OrderService(session)
    return await svc.cancel_order(order_id=order_id, user_id=current_user.id)
