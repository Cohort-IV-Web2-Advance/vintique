from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status

from app.models.cart import Cart
from app.models.product import Product
from app.schemas.cart import CartCreate, CartUpdate


class CartService:
    def __init__(self, db: Session):
        self.db = db

    def get_cart_items(self, user_id: Optional[int] = None) -> List[Cart]:
        query = self.db.query(Cart)
        if user_id:
            query = query.filter(Cart.user_id == user_id)
        return query.all()

    def add_to_cart(self, cart_data: CartCreate, user_id: Optional[int] = None) -> Cart:
        # Check if product exists and has sufficient stock
        product = self.db.query(Product).filter(Product.id == cart_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        if product.stock_quantity < cart_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock"
            )

        # Check if item already exists in cart
        existing_item = self.db.query(Cart).filter(
            Cart.product_id == cart_data.product_id,
            Cart.user_id == user_id
        ).first()

        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + cart_data.quantity
            if product.stock_quantity < new_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient stock for requested quantity"
                )
            existing_item.quantity = new_quantity
            self.db.commit()
            self.db.refresh(existing_item)
            return existing_item
        else:
            # Create new cart item
            cart_item = Cart(
                user_id=user_id,
                product_id=cart_data.product_id,
                quantity=cart_data.quantity
            )
            self.db.add(cart_item)
            self.db.commit()
            self.db.refresh(cart_item)
            return cart_item

    def update_cart_item(self, cart_item_id: int, cart_data: CartUpdate, user_id: Optional[int] = None) -> Cart:
        cart_item = self.db.query(Cart).filter(Cart.id == cart_item_id).first()
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )

        # Check if user owns this cart item
        if user_id and cart_item.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this cart item"
            )

        # Check stock availability
        product = self.db.query(Product).filter(Product.id == cart_item.product_id).first()
        if product.stock_quantity < cart_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock"
            )

        cart_item.quantity = cart_data.quantity
        self.db.commit()
        self.db.refresh(cart_item)
        return cart_item

    def remove_from_cart(self, cart_item_id: int, user_id: Optional[int] = None) -> bool:
        cart_item = self.db.query(Cart).filter(Cart.id == cart_item_id).first()
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )

        # Check if user owns this cart item
        if user_id and cart_item.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to remove this cart item"
            )

        self.db.delete(cart_item)
        self.db.commit()
        return True

    def clear_cart(self, user_id: Optional[int] = None) -> bool:
        query = self.db.query(Cart)
        if user_id:
            query = query.filter(Cart.user_id == user_id)
        
        cart_items = query.all()
        for item in cart_items:
            self.db.delete(item)
        
        self.db.commit()
        return True
