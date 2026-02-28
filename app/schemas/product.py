from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
import re


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, regex="^[a-zA-Z0-9\s\-_.,]+$", description="Product name required (1-255 characters)")
    description: Optional[str] = Field(None, max_length=2000, description="Product description (optional, max 2000 characters)")
    price: Decimal = Field(..., gt=0, le=999999.99, description="Price must be greater than 0 and less than 1,000,000")
    stock_quantity: int = Field(..., ge=0, le=10000, description="Stock quantity must be non-negative and less than 10,000")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate product name."""
        if not v or not v.strip():
            raise ValueError('Product name cannot be empty')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        """Validate product description."""
        if v and not v.strip():
            raise ValueError('Product description cannot be empty if provided')
        return v.strip() if v else None
    
    @validator('price')
    def validate_price(cls, v):
        """Validate price format."""
        # Ensure price has at most 2 decimal places
        if v.as_tuple().exponent < -2:
            raise ValueError('Price cannot have more than 2 decimal places')
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, regex="^[a-zA-Z0-9\s\-_.,]+$", description="Product name (1-255 characters)")
    description: Optional[str] = Field(None, max_length=2000, description="Product description (max 2000 characters)")
    price: Optional[Decimal] = Field(None, gt=0, le=999999.99, description="Price must be greater than 0 and less than 1,000,000")
    stock_quantity: Optional[int] = Field(None, ge=0, le=10000, description="Stock quantity must be non-negative and less than 10,000")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate product name if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Product name cannot be empty if provided')
            return v.strip()
        return v
    
    @validator('description')
    def validate_description(cls, v):
        """Validate product description if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError('Product description cannot be empty if provided')
            return v.strip()
        return v
    
    @validator('price')
    def validate_price(cls, v):
        """Validate price format if provided."""
        if v is not None:
            # Ensure price has at most 2 decimal places
            if v.as_tuple().exponent < -2:
                raise ValueError('Price cannot have more than 2 decimal places')
        return v


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
