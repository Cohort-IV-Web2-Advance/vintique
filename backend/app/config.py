from pydantic_settings import BaseSettings
from typing import Optional, List
import os
import sys


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL")
    
    # MySQL Environment Variables (for docker-compose)
    mysql_root_password: Optional[str] = os.getenv("MYSQL_ROOT_PASSWORD")
    mysql_database: str = os.getenv("MYSQL_DATABASE", "vintique_db")
    mysql_user: str = os.getenv("MYSQL_USER", "vintique_user")
    mysql_password: Optional[str] = os.getenv("MYSQL_PASSWORD")
    
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
    
    # CORS
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    
    # Gunicorn
    gunicorn_workers: int = int(os.getenv("GUNICORN_WORKERS", "3"))
    gunicorn_timeout: int = int(os.getenv("GUNICORN_TIMEOUT", "120"))
    gunicorn_keepalive: int = int(os.getenv("GUNICORN_KEEPALIVE", "2"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
