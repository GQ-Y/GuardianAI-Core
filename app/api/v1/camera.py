from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.camera import CameraInfo
from app.services.camera_service import get_cameras
from app.api.deps import get_db

router = APIRouter()

@router.get("/", response_model=List[CameraInfo])
async def list_cameras(
    db: AsyncSession = Depends(get_db)
):
    """获取摄像头列表"""
    return await get_cameras(db) 