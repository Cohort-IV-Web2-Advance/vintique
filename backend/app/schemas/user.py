from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
import re


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="Valid email address required")
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$", description="Username must be 3-50 characters, alphanumeric and underscore only")
    password: str = Field(..., min_length=8, max_length=128, description="Password must be 8-128 characters")
    shipping_address: Optional[str] = Field(None, max_length=500, description="Shipping address (optional, max 500 characters)")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Strong password validation."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @field_validator('shipping_address')
    @classmethod
    def validate_shipping_address(cls, v):
        """Validate shipping address if provided."""
        if v and not v.strip():
            raise ValueError('Shipping address cannot be empty if provided')
        return v.strip() if v else None


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Valid email address required")
    password: str = Field(..., min_length=1, max_length=128, description="Password required")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Basic password validation for login."""
        if not v or not v.strip():
            raise ValueError('Password cannot be empty')
        return v


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    shipping_address: Optional[str] = None
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountResponse(BaseModel):
    id: int
    user_id: int
    balance: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FundAccountRequest(BaseModel):
    """Schema for funding an account with validation."""
    amount: Decimal = Field(..., gt=0, description="Amount must be greater than 0")
    
    class Config:
        from_attributes = True


class FundAccountResponse(BaseModel):
    """Schema for account funding response."""
    id: int
    user_id: int
    balance: Decimal
    message: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountTransactionRequest(BaseModel):
    """Schema for account transactions (withdraw/deposit)."""
    amount: Decimal = Field(..., gt=0, description="Amount must be greater than 0")
    transaction_type: str = Field(..., pattern="^(deposit|withdraw)$", description="Must be 'deposit' or 'withdraw'")
    
    class Config:
        from_attributes = True
