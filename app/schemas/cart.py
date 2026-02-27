from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CartCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class CartUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class CartResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    product_id: int
    quantity: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
