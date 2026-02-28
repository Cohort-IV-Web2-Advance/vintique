from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
import re


class OrderCreate(BaseModel):
    product_id: int = Field(..., gt=0, description="Valid product ID required")
    quantity: int = Field(..., gt=0, le=100, description="Quantity must be positive and less than 100")
    
    @validator('product_id')
    def validate_product_id(cls, v):
        """Validate product ID."""
        if v <= 0:
            raise ValueError('Product ID must be a positive integer')
        return v


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
