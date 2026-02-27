from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
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
    product_data: ProductCreate,
    image_file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    product_service = ProductService(db)
    return product_service.create_product(product_data, image_file)


@inventory_router.put("/product/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    image_file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
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
