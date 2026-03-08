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


<<<<<<< HEAD
=======
def verify_paystack_signature(payload: bytes, signature: str) -> bool:
    expected = hmac.new(
        settings.paystack_secret_key.encode('utf-8'),
        payload,
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@payment_router.post("/webhook")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("x-paystack-signature", "")

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

        # Step 1 — Find ALL transactions with this reference and update them
        transactions = db.query(Transaction).filter(
            Transaction.reference == reference
        ).all()

        if transactions:
            for transaction in transactions:
                transaction.status = "success"
                transaction.channel = channel
                transaction.paid_at = paid_at
            db.commit()
            logger.info(f"Updated {len(transactions)} transactions to success for reference {reference}")
        else:
            # Fallback — only create if order actually exists
            logger.warning(f"No pending transaction found for reference {reference}, creating new one")
            for order_id in order_ids:
                transaction = Transaction(
                    order_id=order_id,
                    reference=reference,
                    status="success",
                    amount=amount_naira,
                    currency=data.get("currency", "NGN"),
                    channel=channel,
                    paid_at=paid_at
                )
                db.add(transaction)
            db.commit()

        # Step 2 — Update orders to paid AFTER transaction confirmed
        for order_id in order_ids:
            order_service.update_order_status(order_id, "paid")

        # Step 3 — Deduct stock last
        order_service.deduct_stock(order_ids)

        logger.info(f"Payment confirmed for orders {order_ids}, reference {reference}")

    return {"status": "ok"}

>>>>>>> feat/paystack-integration-dev

@payment_router.get("/verify/{reference}")
async def verify_payment_status(
    reference: str,
    db: Session = Depends(get_db)
):
<<<<<<< HEAD
=======
    """
    Verifies payment status by reference.
    Called by frontend after user returns from Paystack payment page.
    Confirms payment with Paystack AND cross-checks with our database.
    """
    # Step 1 — Confirm with Paystack
>>>>>>> feat/paystack-integration-dev
    result = verify_payment(reference)

    if not result["status"]:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=result["message"]
        )

<<<<<<< HEAD
=======
    # Step 2 — Cross check with our database
    transactions = db.query(Transaction).filter(
        Transaction.reference == reference
    ).all()

    order_ids = [t.order_id for t in transactions]
    db_status = transactions[0].status if transactions else "not_found"

    # Step 3 — Return everything frontend needs
>>>>>>> feat/paystack-integration-dev
    return {
        "paid": result["paid"],
        "amount": result["amount"],
        "email": result["email"],
<<<<<<< HEAD
=======
        "reference": reference,
        "order_ids": order_ids,
        "db_status": db_status,
        "message": result["message"]
    }

@payment_router.get("/callback")
async def payment_callback(
    reference: str = None,
    trxref: str = None,
    db: Session = Depends(get_db)
):
    """
    Temporary callback endpoint for testing without frontend.
    In production this will be replaced by Solex's frontend page.
    """
    ref = reference or trxref

    if not ref:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No reference provided"
        )

    result = verify_payment(ref)
    transactions = db.query(Transaction).filter(
        Transaction.reference == ref
    ).all()

    order_ids = [t.order_id for t in transactions]
    db_status = transactions[0].status if transactions else "not_found"

    return {
        "paid": result["paid"],
        "amount": result["amount"],
        "email": result["email"],
        "reference": ref,
        "order_ids": order_ids,
        "db_status": db_status,
>>>>>>> feat/paystack-integration-dev
        "message": result["message"]
    }