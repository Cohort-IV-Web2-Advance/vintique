from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Any
import os
import sys


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL")
    
    # PostgreSQL Environment Variables (for docker-compose)
    postgres_user: str = os.getenv("POSTGRES_USER", "vintique_user")
    postgres_password: Optional[str] = os.getenv("POSTGRES_PASSWORD")
    postgres_db: str = os.getenv("POSTGRES_DB", "vintique_db")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: str = os.getenv("POSTGRES_PORT", "5432")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Cloudinary
    cloudinary_cloud_name: str = os.getenv("CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key: str = os.getenv("CLOUDINARY_API_KEY")
    cloudinary_api_secret: str = os.getenv("CLOUDINARY_API_SECRET")
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Paystack  ← ADD THIS BLOCK
    paystack_secret_key: str = os.getenv("PAYSTACK_SECRET_KEY")
    paystack_public_key: str = os.getenv("PAYSTACK_PUBLIC_KEY")
    payment_callback_url: str = os.getenv("PAYMENT_CALLBACK_URL")

    
    # CORS
    cors_origins: Any = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if not v.strip():  # Handle empty string
                return []
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Gunicorn
    gunicorn_workers: int = int(os.getenv("GUNICORN_WORKERS", "3"))
    gunicorn_timeout: int = int(os.getenv("GUNICORN_TIMEOUT", "120"))
    gunicorn_keepalive: int = int(os.getenv("GUNICORN_KEEPALIVE", "2"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
