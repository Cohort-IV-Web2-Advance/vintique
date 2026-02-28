from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List

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
