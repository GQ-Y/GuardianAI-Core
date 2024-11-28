from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ...database import get_db
from ...schemas import site as schemas
from ...models import SiteGroup, Camera
from ...services import site_service

router = APIRouter()

@router.get(
    "/groups",
    response_model=List[schemas.SiteGroupInfo],
    summary="获取工地分组列表",
    description="获取所有工地分组的基本信息列表"
)
async def get_site_groups(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有工地分组列表
    
    返回:
    - 工地分组列表，包含基本信息
    """
    try:
        groups = await site_service.get_site_groups(db)
        return groups
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取工地分组列表失败: {str(e)}"
        )

@router.get(
    "/groups/{group_id}",
    response_model=schemas.SiteGroupDetail,
    summary="获取工地分组详情",
    description="获取指定工地分组的详细信息，包括关联的摄像头列表"
)
async def get_site_group(
    group_id: str = Path(..., description="工地分组ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取工地分组详情
    
    参数:
    - group_id: 工地分组ID
    
    返回:
    - 工地分组详细信息，包括关联的摄像头列表
    """
    try:
        group = await site_service.get_site_group_detail(db, group_id)
        if not group:
            raise HTTPException(
                status_code=404,
                detail=f"未找到工地分组: {group_id}"
            )
        return group
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取工地分组详情失败: {str(e)}"
        )

@router.post(
    "/groups",
    response_model=schemas.SiteGroupInfo,
    summary="创建工地分组",
    description="创建新的工地分组"
)
async def create_site_group(
    group: schemas.SiteGroupCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建工地分组
    
    参数:
    - group: 工地分组创建参数
        - group_id: 工地分组ID
        - group_name: 工地分组名称
        - description: 描述信息（可选）
    
    返回:
    - 创建成功的工地分组信息
    """
    try:
        existing = await site_service.get_site_group(db, group.group_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"工地分组ID已存在: {group.group_id}"
            )
            
        new_group = await site_service.create_site_group(db, group)
        return new_group
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建工地分组失败: {str(e)}"
        )

@router.put(
    "/groups/{group_id}",
    response_model=schemas.SiteGroupInfo,
    summary="更新工地分组",
    description="更新指定工地分组的信息"
)
async def update_site_group(
    group_id: str = Path(..., description="工地分组ID"),
    group_update: schemas.SiteGroupUpdate = None,
    db: AsyncSession = Depends(get_db)
):
    """
    更新工地分组信息
    
    参数:
    - group_id: 工地分组ID
    - group_update: 更新参数
        - group_name: 工地分组名称（可选）
        - description: 描述信息（可选）
    
    返回:
    - 更新后的工地分组信息
    """
    try:
        existing = await site_service.get_site_group(db, group_id)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"未找到工地分组: {group_id}"
            )
            
        updated_group = await site_service.update_site_group(
            db,
            group_id,
            group_update
        )
        return updated_group
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新工地分组失败: {str(e)}"
        )

@router.delete(
    "/groups/{group_id}",
    summary="删除工地分组",
    description="删除指定的工地分组（仅当分组下没有关联的摄像头时才能删除）"
)
async def delete_site_group(
    group_id: str = Path(..., description="工地分组ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    删除工地分组
    
    参数:
    - group_id: 工地分组ID
    
    返回:
    - 删除成功的确认信息
    
    注意:
    - 只有当工地分组下没有关联的摄像头时才能删除
    """
    try:
        existing = await site_service.get_site_group(db, group_id)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"未找到工地分组: {group_id}"
            )
            
        cameras = await site_service.get_group_cameras(db, group_id)
        if cameras:
            raise HTTPException(
                status_code=400,
                detail="无法删除：该工地分组下还有关联的摄像头"
            )
            
        await site_service.delete_site_group(db, group_id)
        return {"message": f"工地分组 {group_id} 删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除工地分组失败: {str(e)}"
        ) 