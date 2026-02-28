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
        """
        Create a new product with optional image upload.
        
        Args:
            product_data: Product data object with image_file attribute
            
        Returns:
            Product: Created product object
            
        Raises:
            ValueError: If image validation fails
            HTTPException: If product creation fails
        """
        # Handle image upload if provided
        image_url = None
        old_image_url = None  # For cleanup in case of error
        
        try:
            image_file = getattr(product_data, 'image_file', None)
            if image_file and image_file.filename:  # Check if file is actually provided
                upload_result = upload_image(image_file)
                image_url = upload_result.get("secure_url")
            
            # Create product
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
            
        except ValueError as ve:
            # Re-raise validation errors
            raise ValueError(str(ve))
        except Exception as e:
            # If we uploaded an image but failed to create product, try to clean up
            if image_url:
                try:
                    delete_image(image_url)
                except:
                    pass  # Best effort cleanup
            
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create product: {str(e)}"
            )

    def update_product(self, product_id: int, product_data, image_file=None) -> Product:
        """
        Update an existing product with optional image replacement.
        
        Args:
            product_id: ID of product to update
            product_data: Product data object with updated fields
            image_file: Optional new image file
            
        Returns:
            Product: Updated product object
            
        Raises:
            ValueError: If image validation fails
            HTTPException: If product update fails
        """
        product = self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        old_image_url = product.image_url
        new_image_url = old_image_url  # Default to keeping old image

        try:
            # Handle image update if provided
            if image_file and image_file.filename:  # Check if file is actually provided
                upload_result = update_image(image_file)
                new_image_url = upload_result.get("secure_url")
            
            # Update fields
            update_data = product_data.dict(exclude_unset=True) if hasattr(product_data, 'dict') else {}
            for field, value in update_data.items():
                if hasattr(product, field):
                    setattr(product, field, value)
            
            # Update image URL if changed
            if new_image_url != old_image_url:
                product.image_url = new_image_url

            self.db.commit()
            self.db.refresh(product)
            
            # Delete old image from Cloudinary if it was replaced
            if old_image_url and new_image_url != old_image_url:
                try:
                    delete_image(old_image_url)
                except:
                    pass  # Log error but don't fail the update
            
            return product
            
        except ValueError as ve:
            # Re-raise validation errors
            raise ValueError(str(ve))
        except Exception as e:
            # If we uploaded a new image but failed to update, try to clean up
            if new_image_url != old_image_url and new_image_url:
                try:
                    delete_image(new_image_url)
                except:
                    pass  # Best effort cleanup
            
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update product: {str(e)}"
            )

    def delete_product(self, product_id: int) -> bool:
        """
        Delete a product and its associated image from Cloudinary.
        
        Args:
            product_id: ID of product to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            HTTPException: If product not found or deletion fails
        """
        product = self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Store image URL for cleanup
        image_url_to_delete = product.image_url

        try:
            # Delete product from database first
            self.db.delete(product)
            self.db.commit()
            
            # Delete image from Cloudinary if it exists
            if image_url_to_delete:
                try:
                    delete_image(image_url_to_delete)
                except Exception as img_error:
                    # Log error but don't fail the deletion
                    # In production, you'd want to log this properly
                    print(f"Warning: Failed to delete image {image_url_to_delete}: {str(img_error)}")
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete product: {str(e)}"
            )

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
