import hmac
import hashlib
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.order import Transaction
from app.services.order_service import OrderService

logger = logging.getLogger(__name__)

payment_router = APIRouter(prefix="/payments", tags=["payments"])


def verify_paystack_signature(payload: bytes, signature: str) -> bool:
    """
    Verifies the webhook request genuinely came from Paystack.
    Uses HMAC-SHA512 signature check against the secret key.
    """
    expected = hmac.new(
        settings.paystack_secret_key.encode('utf-8'),
        payload,
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@payment_router.post("/webhook")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receives and processes payment events from Paystack.
    This endpoint must remain public — no authentication required.
    Paystack calls this directly after every payment attempt.
    Always returns HTTP 200 so Paystack knows the event was received.
    """
    payload = await request.body()
    signature = request.headers.get("x-paystack-signature", "")

    # Verify request is genuinely from Paystack
    if not verify_paystack_signature(payload, signature):
        logger.warning("Webhook received with invalid signature")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )

    event = json.loads(payload)
    event_type = event.get("event")
    data = event.get("data", {})

    logger.info(f"Paystack webhook received: {event_type}")

    if event_type == "charge.success":
        reference = data.get("reference")
        order_ids = data.get("metadata", {}).get("order_ids", [])
        amount_naira = data.get("amount", 0) / 100
        channel = data.get("channel", "")
        paid_at = data.get("paid_at")

        if not order_ids:
            logger.error(f"Webhook missing order_ids in metadata for reference {reference}")
            return {"status": "ok"}

        order_service = OrderService(db)

        # Update each order status to paid
        for order_id in order_ids:
            order_service.update_order_status(order_id, "paid")

        # Deduct stock after payment confirmed
        order_service.deduct_stock(order_ids)

        # Create transaction record
        transaction = Transaction(
            order_id=order_ids[0],
            reference=reference,
            status="success",
            amount=amount_naira,
            currency=data.get("currency", "NGN"),
            channel=channel,
            paid_at=paid_at
        )
        db.add(transaction)
        db.commit()

        logger.info(f"Payment confirmed for orders {order_ids}, reference {reference}")

    return {"status": "ok"}