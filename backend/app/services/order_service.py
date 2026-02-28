from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from decimal import Decimal

from app.models.order import Order, Transaction
from app.models.product import Product
from app.models.cart import Cart
from app.schemas.order import OrderCreate


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()

    def get_user_orders(self, user_id: int) -> List[Order]:
        return self.db.query(Order).filter(Order.user_id == user_id).all()

    def get_all_orders(self) -> List[Order]:
        return self.db.query(Order).all()

    def create_order(self, order_data: OrderCreate, user_id: int) -> Order:
        # Check if product exists and has sufficient stock
        product = self.db.query(Product).filter(Product.id == order_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        if product.stock_quantity < order_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock"
            )

        # Calculate total amount
        unit_price = product.price
        total_amount = unit_price * order_data.quantity

        # Create order
        order = Order(
            product_id=order_data.product_id,
            user_id=user_id,
            amount=total_amount,
            quantity=order_data.quantity,
            unit_price=unit_price,
            order_status="pending"
        )

        self.db.add(order)
        self.db.flush()  # Get the order ID without committing

        # Create transaction record
        transaction = Transaction(
            order_id=order.id,
            payment_id=None  # Will be set when payment is processed
        )
        self.db.add(transaction)

        # Update product stock
        product.stock_quantity -= order_data.quantity

        # Remove from cart if exists
        cart_item = self.db.query(Cart).filter(
            Cart.product_id == order_data.product_id,
            Cart.user_id == user_id
        ).first()
        if cart_item:
            if cart_item.quantity <= order_data.quantity:
                self.db.delete(cart_item)
            else:
                cart_item.quantity -= order_data.quantity

        self.db.commit()
        self.db.refresh(order)
        return order

    def update_order_status(self, order_id: int, new_status: str) -> Order:
        order = self.get_order_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        order.order_status = new_status
        self.db.commit()
        self.db.refresh(order)
        return order

    def create_transaction(self, order_id: int, payment_id: str) -> Transaction:
        transaction = Transaction(
            order_id=order_id,
            payment_id=payment_id
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
