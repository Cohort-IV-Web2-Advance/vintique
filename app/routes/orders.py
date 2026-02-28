from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService
from app.core.auth import get_current_user
from app.models.user import User

order_router = APIRouter(prefix="/orders", tags=["orders"])


@order_router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order_service = OrderService(db)
    return order_service.create_order(order_data, current_user.id)


@order_router.get("/history", response_model=List[OrderResponse])
def get_order_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order_service = OrderService(db)
    return order_service.get_user_orders(current_user.id)


@order_router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get order by ID with proper authorization.
    
    - Users can only access their own orders
    - Admins can access any order
    """
    # Validate order_id
    if order_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID"
        )
    
    order_service = OrderService(db)
    order = order_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Authorization check: Users can only access their own orders, admins can access any order
    if order.user_id != current_user.id and not current_user.is_admin:
        # Log unauthorized access attempt for security
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"Unauthorized access attempt: User {current_user.id} ({current_user.email}) "
            f"tried to access order {order_id} owned by user {order.user_id}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order
