from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Optional



class TransactionCreate(BaseModel):
    order_id: int
    reference: str
    amount: Decimal
    status: str        # "success" or "failed"
    provider: str = "paystack"
    paid_at: Optional[datetime] = None



class TransactionResponse(BaseModel):
    id: int
    order_id: int
    reference: Optional[str]
    amount: Decimal
    status: str
    provider: str
    paid_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  