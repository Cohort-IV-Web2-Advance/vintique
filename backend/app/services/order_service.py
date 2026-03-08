from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from decimal import Decimal

from app.models.order import Order  
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

    def create_order(self, order_data: OrderCreate, user_id: int) -> List[Order]:
        created_orders = []
        
        try:
            # Loop through every item in order_data.items in a single transaction
            for item in order_data.items:
                # Validate each product exists and has sufficient stock
                product = self.db.query(Product).filter(Product.id == item.product_id).first()
                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Product with ID {item.product_id} not found"
                    )

                if product.stock_quantity < item.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Insufficient stock for product {item.product_id}. Available: {product.stock_quantity}, Requested: {item.quantity}"
                    )

                # Calculate price from the DB (product.price * item.quantity) — never trust the client price
                unit_price = product.price
                total_amount = unit_price * item.quantity

                # Create one Order row per item, all sharing the same shipping_address
                order = Order(
                    product_id=item.product_id,
                    user_id=user_id,
                    amount=total_amount,
                    quantity=item.quantity,
                    unit_price=unit_price,
                    order_status="pending",
                    shipping_address=order_data.shipping_address
                )

                self.db.add(order)
                self.db.flush()  # Get the order ID without committing

                # Create one Transaction row per order
                transaction = Transaction(
                    order_id=order.id,
                    payment_id=None  # Will be set when payment is processed
                )
                self.db.add(transaction)

                # Decrement product.stock_quantity for each item
                product.stock_quantity -= item.quantity

                # Remove each item from the user's cart if it exists
                cart_item = self.db.query(Cart).filter(
                    Cart.product_id == item.product_id,
                    Cart.user_id == user_id
                ).first()
                if cart_item:
                    if cart_item.quantity <= item.quantity:
                        self.db.delete(cart_item)
                    else:
                        cart_item.quantity -= item.quantity

                created_orders.append(order)

            # Commit once at the end of the loop
            self.db.commit()
            
            # Refresh all orders to get the final state
            for order in created_orders:
                self.db.refresh(order)
                
            return created_orders
            
        except Exception as e:
            self.db.rollback()
            raise e

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


