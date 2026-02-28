from pydantic_settings import BaseSettings
from typing import Optional, List
import os
import sys


class Settings(BaseSettings):
    # Database
    database_url: str = "mysql+pymysql://vintique_user:vintique_password@localhost:3306/vintique_db"
    
    # MySQL Environment Variables (for docker-compose)
    mysql_root_password: str = "root_password"
    mysql_database: str = "vintique_db"
    mysql_user: str = "vintique_user"
    mysql_password: str = "vintique_password"
    
    # JWT
    jwt_secret_key: str = "fallback_secret_key_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # Cloudinary
    cloudinary_cloud_name: str = "dxdt9ryza"
    cloudinary_api_key: str = "181989243158131"
    cloudinary_api_secret: str = "ukBeknAHb_avpgRhcuVJH9oBI6o"
    
    # Environment
    environment: str = "development"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Gunicorn
    gunicorn_workers: int = 3
    gunicorn_timeout: int = 120
    gunicorn_keepalive: int = 2
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
