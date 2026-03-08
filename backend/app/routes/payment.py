import hmac
import hashlib
import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.order import Transaction
from app.services.order_service import OrderService
from app.services.payment_service import verify_payment

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
        paid_at_str = data.get("paid_at")
        paid_at = datetime.strptime(paid_at_str, "%Y-%m-%dT%H:%M:%S.%fZ") if paid_at_str else None

        if not order_ids:
            logger.error(f"Webhook missing order_ids in metadata for reference {reference}")
            return {"status": "ok"}

        order_service = OrderService(db)

        # Step 1 — Find and update transaction FIRST
        transaction = db.query(Transaction).filter(
            Transaction.reference == reference
        ).all()

        if transaction:
            transaction.status = "success"
            transaction.channel = channel
            transaction.paid_at = paid_at
            db.commit()
        else:
            # Fallback — create transaction if not found
            logger.warning(f"No pending transaction found for reference {reference}, creating new one")
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

        # Step 2 — Only update orders to paid AFTER transaction is confirmed
        for order_id in order_ids:
            order_service.update_order_status(order_id, "paid")

        # Step 3 — Deduct stock last
        order_service.deduct_stock(order_ids)

        logger.info(f"Payment confirmed for orders {order_ids}, reference {reference}")

    return {"status": "ok"}


@payment_router.get("/verify/{reference}")
async def verify_payment_status(
    reference: str,
    db: Session = Depends(get_db)
):
    """
    Verifies payment status by reference.
    Called by frontend after user returns from Paystack payment page.
    """
    result = verify_payment(reference)

    if not result["status"]:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=result["message"]
        )

    return {
        "paid": result["paid"],
        "amount": result["amount"],
        "email": result["email"],
        "message": result["message"]
    }