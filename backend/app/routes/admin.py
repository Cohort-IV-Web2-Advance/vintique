from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Union, Optional
from pydantic import BaseModel

from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.user import UserResponse
from app.schemas.order import OrderResponse
from app.services.product_service import ProductService
from app.services.user_service import UserService
from app.services.order_service import OrderService
from app.core.auth import get_current_admin_user
from app.models.user import User

admin_router = APIRouter(prefix="/admin", tags=["admin"])


class UserIdentifier(BaseModel):
    user_id: Union[int, str]  # Can be ID (int) or username (str)


class UserAccountAction(BaseModel):
    user_id: Union[int, str]  # Can be ID (int) or username (str)
    action: str  # Options: "delete", "suspend", "reactivate"
    reason: Optional[str] = None  # Optional reason for the action


@admin_router.get("/orders", response_model=List[OrderResponse])
def get_all_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    order_service = OrderService(db)
    return order_service.get_all_orders()


@admin_router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user_service = UserService(db)
    return user_service.get_all_users()


@admin_router.get("/products", response_model=List[ProductResponse])
def get_all_products_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    product_service = ProductService(db)
    return product_service.get_all_products()


@admin_router.patch("/users/{identifier}/make-admin", response_model=UserResponse)
def make_user_admin(
    identifier: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
   
    
    if current_user.id == identifier or current_user.username == User.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already an admin"
        )

    user = db.query(User).filter(User.id == identifier).first() or db.query(User).filter(User.username == identifier).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {identifier} {user.username} not found"
        )

    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{user.username}' is already an admin"
        )

    user.is_admin = True
    db.commit()
    db.refresh(user)

    return user


@admin_router.post("/users/account-action", response_model=dict)
def manage_user_account(
    action_data: UserAccountAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Manage user accounts with actions: delete, suspend, reactivate
    
    Args:
        action_data: Contains user_id (int or str), action (delete/suspend/reactivate), and optional reason
    
    Returns:
        dict: Success message with details of the action performed
    """
    user_service = UserService(db)
    
    # Find user by ID or username
    user = None
    if isinstance(action_data.user_id, int):
        user = db.query(User).filter(User.id == action_data.user_id).first()
    elif isinstance(action_data.user_id, str):
        # Try to find by ID first (in case string represents a number)
        try:
            user_id = int(action_data.user_id)
            user = db.query(User).filter(User.id == user_id).first()
        except ValueError:
            pass
        
        # If not found by ID, try username
        if not user:
            user = db.query(User).filter(User.username == action_data.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with identifier '{action_data.user_id}' not found"
        )
    
    # Prevent admin from acting on themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot perform this action on your own account"
        )
    
    # Perform the requested action
    if action_data.action == "delete":
        # Soft delete by setting is_active to False
        user.is_active = False
        user.is_deleted = True
        db.commit()
        return {
            "message": f"User '{user.username}' (ID: {user.id}) has been deleted successfully",
            "action": "delete",
            "user_id": user.id,
            "username": user.username,
            "reason": action_data.reason
        }
    
    elif action_data.action == "suspend":
        if user.is_suspended:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{user.username}' is already suspended"
            )
        
        user.is_suspended = True
        user.is_active = False
        db.commit()
        return {
            "message": f"User '{user.username}' (ID: {user.id}) has been suspended successfully",
            "action": "suspend",
            "user_id": user.id,
            "username": user.username,
            "reason": action_data.reason
        }
    
    elif action_data.action == "reactivate":
        if not user.is_suspended and not (user.is_deleted or not user.is_active):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{user.username}' is already active"
            )
        
        user.is_suspended = False
        user.is_active = True
        user.is_deleted = False
        db.commit()
        return {
            "message": f"User '{user.username}' (ID: {user.id}) has been reactivated successfully",
            "action": "reactivate",
            "user_id": user.id,
            "username": user.username,
            "reason": action_data.reason
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action '{action_data.action}'. Supported actions: delete, suspend, reactivate"
        )



# Inventory Management Routes
inventory_router = APIRouter(prefix="/inventory", tags=["inventory"])


@inventory_router.post("/product", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    name: str = Form(..., description="Product name (required)"),
    description: str = Form(None, description="Product description (optional)"),
    price: float = Form(..., description="Product price (required)"),
    stock_quantity: int = Form(..., description="Stock quantity (required)"),
    image_file: UploadFile = File(..., description="Product image (required)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new product with image upload.
    
    Image upload is required and will be validated for:
    - File type (jpg, jpeg, png, webp only)
    - File size (max 5MB)
    - MIME type validation
    """
    from decimal import Decimal
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Validate form data
        if not name or not name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product name is required"
            )
        
        if price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price must be greater than 0"
            )
        
        if stock_quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock quantity cannot be negative"
            )
        
        # Validate image file is provided
        if not image_file or not image_file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product image is required"
            )
        
        # Create product data object
        class ProductData:
            def __init__(self, name, description, price, stock_quantity, image_file):
                self.name = name.strip()
                self.description = description.strip() if description else None
                self.price = Decimal(str(price))
                self.stock_quantity = stock_quantity
                self.image_file = image_file
        
        product_data = ProductData(
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            image_file=image_file
        )
        
        # Create product using service
        product_service = ProductService(db)
        product = product_service.create_product(product_data)
        
        logger.info(f"Product created successfully: ID {product.id}, Name: {product.name}")
        return product
        
    except ValueError as ve:
        # Handle validation errors from image upload
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Failed to create product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )


@inventory_router.put("/product/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    stock_quantity: int = Form(None),
    image_file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    from app.schemas.product import ProductUpdate
    from decimal import Decimal
    
    # Create ProductUpdate object from form data (only include provided fields)
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if price is not None:
        update_data["price"] = Decimal(str(price))
    if stock_quantity is not None:
        update_data["stock_quantity"] = stock_quantity
    
    product_data = ProductUpdate(**update_data)
    
    product_service = ProductService(db)
    return product_service.update_product(product_id, product_data, image_file)


@inventory_router.delete("/product/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    product_service = ProductService(db)
    product_service.delete_product(product_id)


    
