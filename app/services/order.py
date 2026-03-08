from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.social import Order
from app.models.offer import PriceOffer, OfferStatus
from app.models.notification import NotificationType
from app.core.enums import OrderStatus
from app.core.exceptions import ForbiddenError, ConflictError
from app.repositories.order import OrderRepository
from app.repositories.offer import OfferRepository
from app.services.notification import NotificationService


class OrderService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.order_repo = OrderRepository(session)
        self.offer_repo = OfferRepository(session)

    async def create_order(
        self, *, item_id: UUID, buyer_id: UUID, seller_id: UUID, inquiry_message: str | None
    ) -> Order:
        return await self.order_repo.create(
            item_id=item_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            status=OrderStatus.inquiry,
            inquiry_message=inquiry_message,
        )

    async def make_offer(
        self, *, order_id: UUID, offered_by: UUID, amount_sar: Decimal, message: str | None
    ) -> PriceOffer:
        order = await self.order_repo.get_or_404(order_id)
        if order.status not in (OrderStatus.inquiry, OrderStatus.reserved):
            raise ConflictError("Order is not in a negotiable state")
        if offered_by not in (order.buyer_id, order.seller_id):
            raise ForbiddenError("Not a party to this order")

        # Only one pending offer at a time
        await self.offer_repo.supersede_pending(order_id)

        offer = await self.offer_repo.create(
            order_id=order_id,
            offered_by=offered_by,
            amount_sar=amount_sar,
            message=message,
            status=OfferStatus.pending,
        )

        # Notify the other party
        receiver_id = order.seller_id if offered_by == order.buyer_id else order.buyer_id
        notif_svc = NotificationService(self.session)
        await notif_svc.notify(
            user_id=receiver_id,
            type=NotificationType.offer_received,
            title_ar="عرض سعر جديد",
            title_en="New Price Offer",
            body_ar=f"عرض سعر جديد: {amount_sar} ر.س",
            body_en=f"New offer: {amount_sar} SAR",
            data={"order_id": str(order_id), "offer_id": str(offer.id)},
        )
        return offer

    async def accept_offer(self, *, offer_id: UUID, user_id: UUID) -> PriceOffer:
        offer = await self.offer_repo.get_or_404(offer_id)
        order = await self.order_repo.get_or_404(offer.order_id)
        if offer.status != OfferStatus.pending:
            raise ConflictError("Offer is no longer pending")
        # Only the non-offering party can accept
        if offer.offered_by == user_id:
            raise ForbiddenError("Cannot accept your own offer")
        if user_id not in (order.buyer_id, order.seller_id):
            raise ForbiddenError("Not a party to this order")

        await self.offer_repo.update(offer_id, status=OfferStatus.accepted)
        await self.order_repo.update(offer.order_id, status=OrderStatus.reserved)

        notif_svc = NotificationService(self.session)
        await notif_svc.notify(
            user_id=offer.offered_by,
            type=NotificationType.offer_accepted,
            title_ar="تم قبول عرضك",
            title_en="Offer Accepted",
            body_ar=f"تم قبول عرضك بـ {offer.amount_sar} ر.س",
            body_en=f"Your offer of {offer.amount_sar} SAR was accepted",
            data={"order_id": str(offer.order_id)},
        )
        return await self.offer_repo.get(offer_id)

    async def reject_offer(self, *, offer_id: UUID, user_id: UUID) -> PriceOffer:
        offer = await self.offer_repo.get_or_404(offer_id)
        order = await self.order_repo.get_or_404(offer.order_id)
        if offer.status != OfferStatus.pending:
            raise ConflictError("Offer is no longer pending")
        if offer.offered_by == user_id:
            raise ForbiddenError("Cannot reject your own offer")
        if user_id not in (order.buyer_id, order.seller_id):
            raise ForbiddenError("Not a party to this order")

        await self.offer_repo.update(offer_id, status=OfferStatus.rejected)

        notif_svc = NotificationService(self.session)
        await notif_svc.notify(
            user_id=offer.offered_by,
            type=NotificationType.offer_rejected,
            title_ar="تم رفض عرضك",
            title_en="Offer Rejected",
            body_ar="تم رفض عرضك",
            body_en="Your offer was rejected",
            data={"order_id": str(offer.order_id)},
        )
        return await self.offer_repo.get(offer_id)

    async def counter_offer(
        self, *, offer_id: UUID, user_id: UUID, amount_sar: Decimal, message: str | None
    ) -> PriceOffer:
        offer = await self.offer_repo.get_or_404(offer_id)
        if offer.offered_by == user_id:
            raise ForbiddenError("Cannot counter your own offer")
        return await self.make_offer(
            order_id=offer.order_id,
            offered_by=user_id,
            amount_sar=amount_sar,
            message=message,
        )

    async def cancel_order(self, *, order_id: UUID, user_id: UUID) -> Order:
        order = await self.order_repo.get_or_404(order_id)
        if user_id not in (order.buyer_id, order.seller_id):
            raise ForbiddenError()
        if order.status == OrderStatus.completed:
            raise ConflictError("Cannot cancel a completed order")
        await self.offer_repo.supersede_pending(order_id)
        await self.order_repo.update(order_id, status=OrderStatus.cancelled)
        return await self.order_repo.get(order_id)
