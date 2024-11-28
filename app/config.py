from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # 基础配置
    APP_NAME: str = "Safety Inspection System"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./safety.db"
    
    # AI配置
    ZHIPU_API_KEY: Optional[str] = None
    
    # 图片存储配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ALLOWED_HOSTS: list = ["*"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    
    class Config:
        env_file = ".env"

settings = Settings() 