from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
import uuid

from ..models.site import Camera
from ..models.hazard import Hazard
from ..schemas import (
    CameraCreate,
    CameraUpdate
)

async def get_camera(db: AsyncSession, camera_id: str) -> Optional[Camera]:
    """获取摄像头信息"""
    stmt = (
        select(Camera)
        .options(
            selectinload(Camera.scenes),
            selectinload(Camera.hazards)
        )
        .where(Camera.camera_id == camera_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_camera_hazards(db: AsyncSession, camera_id: str) -> List[Hazard]:
    """获取摄像头的隐患记录"""
    stmt = (
        select(Hazard)
        .where(Hazard.camera_id == camera_id)
        .where(Hazard.status == 'active')
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_camera_status(db: AsyncSession, camera_id: str):
    """获取摄像头状态"""
    camera = await get_camera(db, camera_id)
    if not camera:
        return None
        
    hazards = await get_camera_hazards(db, camera_id)
    
    return {
        "camera": {
            "camera_id": camera.camera_id,
            "camera_name": camera.camera_name,
            "location": camera.location,
            "status": camera.status
        },
        "active_hazards": len(hazards),
        "scenes": [scene.scene_id for scene in camera.scenes]
    } 

async def get_site_group(db: AsyncSession, group_id: str):
    """获取工地组信息"""
    stmt = select(SiteGroup).where(SiteGroup.group_id == group_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_camera(db: AsyncSession, camera_data: CameraCreate) -> Camera:
    """创建新摄像头"""
    # 创建摄像头记录
    camera = Camera(
        camera_id=camera_data.camera_id,
        camera_name=camera_data.camera_name,
        group_id=camera_data.group_id,
        location=camera_data.location,
        description=camera_data.description,
        status=camera_data.status
    )
    db.add(camera)
    await db.flush()
    
    # 创建场景关联
    for scene_id in camera_data.scenes:
        scene = CameraScene(
            camera_id=camera.camera_id,
            scene_id=scene_id
        )
        db.add(scene)
    
    await db.commit()
    return camera

async def update_camera(
    db: AsyncSession,
    camera_id: str,
    camera_update: CameraUpdate
) -> Camera:
    """更新摄像头信息"""
    camera = await get_camera(db, camera_id)
    
    # 更新基本信息
    if camera_update.camera_name is not None:
        camera.camera_name = camera_update.camera_name
    if camera_update.group_id is not None:
        camera.group_id = camera_update.group_id
    if camera_update.location is not None:
        camera.location = camera_update.location
    if camera_update.description is not None:
        camera.description = camera_update.description
    if camera_update.status is not None:
        camera.status = camera_update.status
        
    # 更新场景关联
    if camera_update.scenes is not None:
        # 删除现有关联
        await db.execute(
            delete(CameraScene).where(CameraScene.camera_id == camera_id)
        )
        # 创建新关联
        for scene_id in camera_update.scenes:
            scene = CameraScene(
                camera_id=camera_id,
                scene_id=scene_id
            )
            db.add(scene)
    
    await db.commit()
    await db.refresh(camera)
    return camera

async def delete_camera(db: AsyncSession, camera_id: str):
    """删除摄像头"""
    # 删除关联的场景
    await db.execute(
        delete(CameraScene).where(CameraScene.camera_id == camera_id)
    )
    
    # 删除关联的隐患记录
    await db.execute(
        delete(Hazard).where(Hazard.camera_id == camera_id)
    )
    
    # 删除摄像头
    await db.execute(
        delete(Camera).where(Camera.camera_id == camera_id)
    )
    
    await db.commit() 