"""Configuration settings for ArtForge."""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "sqlite:///./art_forge.db"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8003
    
    # Application
    app_name: str = "ArtForge"
    app_url: str = "https://forge-freedom.com/art"
    
    # Upload Settings
    upload_dir: str = "data/uploads"
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: str = "jpg,jpeg,png,gif,webp"
    
    class Config:
        env_file = ".env"


settings = Settings()

