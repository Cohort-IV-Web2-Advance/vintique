from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.utils.cloudinary import upload_image, update_image, delete_image


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_all_products(self) -> List[Product]:
        return self.db.query(Product).all()

    def create_product(self, product_data) -> Product:
        # Handle image upload if provided
        image_url = None
        image_file = product_data.image_file
        if image_file:
            upload_result = upload_image(image_file)
            image_url = upload_result.get("secure_url")

        product = Product(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity,
            image_url=image_url
        )

        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update_product(self, product_id: int, product_data: ProductUpdate, image_file=None) -> Product:
        product = self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Update fields
        update_data = product_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        # Handle image update if provided
        if image_file:
            # Delete old image if exists
            if product.image_url:
                delete_image(product.image_url)
            
            # Upload new image
            upload_result = upload_image(image_file)
            product.image_url = upload_result.get("secure_url")

        self.db.commit()
        self.db.refresh(product)
        return product

    def delete_product(self, product_id: int) -> bool:
        product = self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Delete image from Cloudinary if exists
        if product.image_url:
            delete_image(product.image_url)

        self.db.delete(product)
        self.db.commit()
        return True

    def update_stock(self, product_id: int, quantity_change: int) -> Product:
        product = self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        new_quantity = product.stock_quantity + quantity_change
        if new_quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock"
            )

        product.stock_quantity = new_quantity
        self.db.commit()
        self.db.refresh(product)
        return product
