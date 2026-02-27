from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class OrderCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    amount: Decimal
    quantity: int
    unit_price: Decimal
    order_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    id: int
    order_id: int
    payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
