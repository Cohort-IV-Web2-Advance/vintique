import cloudinary
import cloudinary.uploader
from app.config import settings
import re
from typing import Optional

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret
)

# Allowed file types and max size (5MB)
ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 5MB in bytes


def validate_image_file(image_file) -> None:
    """
    Validate uploaded image file for type, size, and format.
    
    Args:
        image_file: Uploaded file object
        
    Raises:
        ValueError: If file validation fails
    """
    if not image_file or not hasattr(image_file, 'filename'):
        raise ValueError("No file provided")
    
    # Check file extension
    filename = image_file.filename.lower()
    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise ValueError(f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # Check MIME type
    if hasattr(image_file, 'content_type') and image_file.content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Invalid MIME type. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}")
    
    # Check file size
    if hasattr(image_file, 'size') and image_file.size > MAX_FILE_SIZE:
        raise ValueError(f"File too large. Maximum size: 5MB")
    
    # Reset file pointer if it was read
    if hasattr(image_file, 'seek'):
        image_file.seek(0)


def upload_image(image_file) -> dict:
    """
    Upload an image to Cloudinary and return the upload result.
    
    Args:
        image_file: Uploaded file object
        
    Returns:
        dict: Cloudinary upload result containing secure_url and other metadata
        
    Raises:
        ValueError: If file validation fails
        Exception: If upload fails
    """
    try:
        # Validate file before upload
        validate_image_file(image_file)
        
        # Read file content
        file_content = image_file.file.read()
        
        # Double-check file size
        if len(file_content) > MAX_FILE_SIZE:
            raise ValueError(f"File too large. Maximum size: 5MB")
        
        # Upload to Cloudinary with validation
        result = cloudinary.uploader.upload(
            file_content,
            folder="vintique/products",
            resource_type="image",
            allowed_formats=["jpg", "jpeg", "png", "webp"],
            quality="auto",
            fetch_format="auto",
            format="auto",  # Let Cloudinary determine format
            transformation=[
                {"quality": "auto"},
                {"fetch_format": "auto"}
            ]
        )
        
        return result
    except ValueError as ve:
        raise ValueError(f"Validation error: {str(ve)}")
    except Exception as e:
        raise Exception(f"Failed to upload image: {str(e)}")


def update_image(image_file, public_id: str = None) -> dict:
    """
    Update an existing image in Cloudinary or upload a new one.
    
    Args:
        image_file: Uploaded file object
        public_id: Optional public_id of the image to replace
        
    Returns:
        dict: Cloudinary upload result
        
    Raises:
        ValueError: If file validation fails
        Exception: If upload fails
    """
    try:
        # Validate file before upload
        validate_image_file(image_file)
        
        file_content = image_file.file.read()
        
        # Double-check file size
        if len(file_content) > MAX_FILE_SIZE:
            raise ValueError(f"File too large. Maximum size: 5MB")
        
        upload_options = {
            "file_content": file_content,
            "folder": "vintique/products",
            "resource_type": "image",
            "allowed_formats": ["jpg", "jpeg", "png", "webp"],
            "quality": "auto",
            "fetch_format": "auto",
            "format": "auto"
        }
        
        # If public_id is provided, overwrite the existing image
        if public_id:
            upload_options["public_id"] = public_id
            upload_options["overwrite"] = True
        
        result = cloudinary.uploader.upload(**upload_options)
        return result
    except ValueError as ve:
        raise ValueError(f"Validation error: {str(ve)}")
    except Exception as e:
        raise Exception(f"Failed to update image: {str(e)}")


def delete_image(image_url: str) -> bool:
    """
    Delete an image from Cloudinary using its URL.
    
    Args:
        image_url: The secure_url of the image to delete
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        Exception: If deletion fails
    """
    try:
        if not image_url:
            return True  # Nothing to delete
        
        # Extract public_id from the URL
        # Cloudinary URL format: https://res.cloudinary.com/cloud_name/image/upload/v1234567890/folder/public_id.format
        parts = image_url.split('/')
        if len(parts) < 2:
            raise Exception("Invalid image URL format")
        
        # Find the version and extract everything after it
        version_part = None
        for part in parts:
            if part.startswith('v') and part[1:].isdigit():
                version_part = part
                break
        
        if not version_part:
            raise Exception("Could not find version in image URL")
        
        version_index = parts.index(version_part)
        public_id_parts = parts[version_index + 1:]
        public_id = '/'.join(public_id_parts)
        
        # Remove file extension
        if '.' in public_id:
            public_id = public_id.rsplit('.', 1)[0]
        
        # Delete the image
        result = cloudinary.uploader.destroy(public_id, resource_type="image")
        
        return result.get("result") == "ok"
    except Exception as e:
        raise Exception(f"Failed to delete image: {str(e)}")
