from pydantic_settings import BaseSettings
from typing import Optional
import os

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    # 基础配置
    BASE_DIR: str = BASE_DIR
    APP_NAME: str = "Construction Safety Monitor"
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
    LOG_DIR: str = os.path.join(BASE_DIR, 'logs')
    LOG_LEVEL: str = "DEBUG"  # 可选: DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # 阶跃星辰API配置
    STEPAI_API_KEY: Optional[str] = '5jPRWBGQrYro09oIzxHOZwGjQFjg3eOqSesK1fXj1z0ELIYzDKYPBYw5k7HIAu7fW'
    STEPAI_API_URL: str = "https://api.stepfun.com/v1/chat/completions"
    
    # 确保日志目录存在
    @property
    def ensure_log_dir(self):
        if not os.path.exists(self.LOG_DIR):
            os.makedirs(self.LOG_DIR)
        return self.LOG_DIR
    
    class Config:
        env_file = ".env"

settings = Settings() 