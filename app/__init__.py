from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from logging.config import dictConfig

from .config import settings
from .api.routes import api_router

# 配置日志
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
            "formatter": "default",
            "level": "INFO"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file"]
    }
}

dictConfig(logging_config)

def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title=settings.APP_NAME,
        description="建筑工地安全监控智能诊断分析系统",
        version="2.0.0"
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 挂载静态文件
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
    
    # 注册路由
    app.include_router(api_router, prefix="/api/v1")
    
    # 添加根路由
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Safety Inspection System",
            "version": "1.0.0",
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        }
    
    return app 