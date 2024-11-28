from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from datetime import datetime

from ..models import SiteGroup, Camera
from ..schemas import (
    SiteGroupCreate,
    SiteGroupUpdate,
    SiteGroupInfo,
    SiteGroupDetail
)

async def get_site_groups(db: AsyncSession) -> List[SiteGroup]:
    """获取所有工地分组"""
    stmt = select(SiteGroup).order_by(SiteGroup.group_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_site_group(db: AsyncSession, group_id: str) -> Optional[SiteGroup]:
    """获取工地分组基本信息"""
    stmt = select(SiteGroup).where(SiteGroup.group_id == group_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_site_group_detail(
    db: AsyncSession,
    group_id: str
) -> Optional[dict]:
    """获取工地分组详细信息"""
    group = await get_site_group(db, group_id)
    if not group:
        return None
        
    # 获取关联的摄像头
    cameras = await get_group_cameras(db, group_id)
    
    return {
        "group_id": group.group_id,
        "group_name": group.group_name,
        "description": group.description,
        "cameras": cameras,
        "created_at": group.created_at,
        "updated_at": group.updated_at
    }

async def get_group_cameras(
    db: AsyncSession,
    group_id: str
) -> List[Camera]:
    """获取工地分组下的摄像头"""
    stmt = select(Camera).where(Camera.group_id == group_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_site_group(
    db: AsyncSession,
    group_data: SiteGroupCreate
) -> SiteGroup:
    """创建工地分组"""
    group = SiteGroup(
        group_id=group_data.group_id,
        group_name=group_data.group_name,
        description=group_data.description
    )
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group

async def update_site_group(
    db: AsyncSession,
    group_id: str,
    group_update: SiteGroupUpdate
) -> SiteGroup:
    """更新工地分组"""
    group = await get_site_group(db, group_id)
    
    if group_update.group_name is not None:
        group.group_name = group_update.group_name
    if group_update.description is not None:
        group.description = group_update.description
        
    await db.commit()
    await db.refresh(group)
    return group

async def delete_site_group(db: AsyncSession, group_id: str):
    """删除工地分组"""
    await db.execute(
        delete(SiteGroup).where(SiteGroup.group_id == group_id)
    )
    await db.commit() 