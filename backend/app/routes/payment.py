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



@payment_router.get("/verify/{reference}")
async def verify_payment_status(
    reference: str,
    db: Session = Depends(get_db)
):
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