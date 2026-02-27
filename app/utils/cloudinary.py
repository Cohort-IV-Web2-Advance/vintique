import cloudinary
import cloudinary.uploader
from app.config import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret
)


def upload_image(image_file) -> dict:
    """
    Upload an image to Cloudinary and return the upload result.
    
    Args:
        image_file: Uploaded file object
        
    Returns:
        dict: Cloudinary upload result containing secure_url and other metadata
    """
    try:
        # Read file content
        file_content = image_file.file.read()
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file_content,
            folder="vintique/products",
            resource_type="image",
            allowed_formats=["jpg", "jpeg", "png", "webp"],
            quality="auto",
            fetch_format="auto"
        )
        
        return result
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
    """
    try:
        file_content = image_file.file.read()
        
        upload_options = {
            "file_content": file_content,
            "folder": "vintique/products",
            "resource_type": "image",
            "allowed_formats": ["jpg", "jpeg", "png", "webp"],
            "quality": "auto",
            "fetch_format": "auto"
        }
        
        # If public_id is provided, overwrite the existing image
        if public_id:
            upload_options["public_id"] = public_id
            upload_options["overwrite"] = True
        
        result = cloudinary.uploader.upload(**upload_options)
        return result
    except Exception as e:
        raise Exception(f"Failed to update image: {str(e)}")


def delete_image(image_url: str) -> bool:
    """
    Delete an image from Cloudinary using its URL.
    
    Args:
        image_url: The secure_url of the image to delete
        
    Returns:
        bool: True if deletion was successful
    """
    try:
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
