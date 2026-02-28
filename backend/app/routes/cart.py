from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.cart import CartCreate, CartUpdate, CartResponse
from app.services.cart_service import CartService
from app.core.auth import get_current_user
from app.models.user import User

cart_router = APIRouter(prefix="/cart", tags=["cart"])


@cart_router.post("/add", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    cart_data: CartCreate, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    cart_service = CartService(db)
    user_id = current_user.id if current_user else None
    return cart_service.add_to_cart(cart_data, user_id)


@cart_router.patch("/update-qty/{cart_item_id}", response_model=CartResponse)
def update_cart_quantity(
    cart_item_id: int,
    cart_data: CartUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    cart_service = CartService(db)
    user_id = current_user.id if current_user else None
    return cart_service.update_cart_item(cart_item_id, cart_data, user_id)


@cart_router.get("/", response_model=List[CartResponse])
def get_cart_items(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    cart_service = CartService(db)
    user_id = current_user.id if current_user else None
    return cart_service.get_cart_items(user_id)


@cart_router.delete("/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    cart_service = CartService(db)
    user_id = current_user.id if current_user else None
    cart_service.remove_from_cart(cart_item_id, user_id)
