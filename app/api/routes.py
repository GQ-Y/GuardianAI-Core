from fastapi import APIRouter
from .endpoints import camera, site

api_router = APIRouter()

# 注册摄像头相关路由
api_router.include_router(
    camera.router,
    prefix="/camera",
    tags=["camera"]
)

# 注册工地分组相关路由
api_router.include_router(
    site.router,
    prefix="/site",
    tags=["site"]
) 