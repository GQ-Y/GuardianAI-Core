from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Path, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import aiofiles
import os

from ...database import get_db
from ...schemas import (
    CameraBase,
    CameraCreate,
    CameraUpdate,
    SiteGroupInfo
)
from ...services import camera_service, ai_service
from ...config import settings
from ...models import Camera, CameraScene

router = APIRouter()

@router.get(
    "/",
    response_model=List[CameraBase],
    summary="获取摄像头列表",
    description="获取所有摄像头的基本信息列表，包括关联的场景和当前活跃隐患数量"
)
async def get_cameras(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有摄像头列表
    
    返回:
    - 摄像头列表，每个摄像头包含:
        - camera_id: 摄像头ID
        - camera_name: 摄像头名称
        - group_id: 所属工地分组
        - location: 安装位置
        - status: 摄像头状态
        - scenes: 关联的场景列表
        - active_hazards: 当前活跃隐患数量
    """
    try:
        cameras = await camera_service.get_cameras(db)
        return cameras
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取摄像头列表失败: {str(e)}"
        )

@router.post(
    "/frame/{camera_id}",
    summary="上传摄像头图片",
    description="上传摄像头拍摄的图片并进行AI分析，识别潜在安全隐患"
)
async def upload_camera_frame(
    camera_id: str = Path(..., description="摄像头ID"),
    file: UploadFile = File(..., description="图片文件，支持jpg/png格式"),
    db: AsyncSession = Depends(get_db)
):
    """
    上传摄像头图片并进行分析
    
    参数:
    - camera_id: 摄像头ID
    - file: 图片文件，要求:
        - 格式: jpg/png
        - 大小: 不超过5MB
        - 分辨率: 建议1920x1080
    
    返回:
    - 分析结果，包含:
        - 已存在隐患的状态更新
        - 新发现的隐患信息
        - 语音警告内容
    
    注意:
    - 图片会被保存在服务器上
    - 分析过程可能需要几秒钟
    """
    try:
        # 验证文件格式
        if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise HTTPException(
                status_code=400,
                detail="只支持jpg/png格式的图片"
            )
            
        # 保存图片
        upload_dir = os.path.join(settings.UPLOAD_DIR, camera_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{file.filename}")
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
            
        # 获取摄像头信息
        camera = await camera_service.get_camera(db, camera_id)
        if not camera:
            raise HTTPException(
                status_code=404,
                detail=f"未找到摄像头: {camera_id}"
            )
            
        # 进行AI分析
        analysis_result = await ai_service.analyze_image(
            db,
            camera,
            file_path
        )
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"图片分析失败: {str(e)}"
        )

@router.get(
    "/hazards/{camera_id}",
    summary="获取摄像头隐患",
    description="获取指定摄像头的所有活跃隐患记录"
)
async def get_camera_hazards(
    camera_id: str = Path(..., description="摄像头ID"),
    status: str = Query(None, description="隐患状态筛选: active-活跃, resolved-已解决"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取摄像头的隐患记录
    
    参数:
    - camera_id: 摄像头ID
    - status: 隐患状态筛选（可选）
    
    返回:
    - 隐患记录列表，每条记录包含:
        - hazard_id: 隐患ID
        - scene_id: 关联的场景
        - violation_type: 违规类型
        - risk_level: 风险等级
        - status: 当前状态
        - detected_at: 发现时间
        - resolved_at: 解决时间（如果已解决）
    """
    try:
        hazards = await camera_service.get_camera_hazards(db, camera_id, status)
        return hazards
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取隐患记录失败: {str(e)}"
        )

@router.get(
    "/status/{camera_id}",
    summary="获取摄像头状态",
    description="获取指定摄像头的当前状态信息，包括活跃隐患数量和关联场景"
)
async def get_camera_status(
    camera_id: str = Path(..., description="摄像头ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取摄像头状态
    
    参数:
    - camera_id: 摄像头ID
    
    返回:
    - 摄像头状态信息:
        - 基本信息（ID、名称、位置等）
        - 当前活跃隐患数量
        - 关联的场景列表
    """
    try:
        status = await camera_service.get_camera_status(db, camera_id)
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"未找到摄像头: {camera_id}"
            )
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取摄像头状态失败: {str(e)}"
        )

@router.post(
    "/",
    response_model=CameraBase,
    summary="创建摄像头",
    description="创建新的摄像头，并关联到指定的工地分组和场景"
)
async def create_camera(
    camera: CameraCreate = Body(..., description="摄像头创建参数"),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新摄像头
    
    参数:
    - camera: 摄像头创建参数
        - camera_id: 摄像头ID（唯一标识）
        - camera_name: 摄像头名称
        - group_id: 所属工地分组ID
        - location: 安装位置
        - description: 描述信息（可选）
        - status: 状态（默认为active）
        - scenes: 关联的场景ID列表
    
    返回:
    - 创建成功的摄像头信息，包含:
        - 基本信息
        - 关联的场景列表
        - 活跃隐患数量（初始为0）
        - 创建和更新时间
    
    注意:
    - camera_id 必须是唯一的
    - group_id 必须是已存在的工地分组
    - scenes 中的场景ID必须是有效的
    """
    try:
        # 检查工地组是否存在
        site_group = await camera_service.get_site_group(db, camera.group_id)
        if not site_group:
            raise HTTPException(
                status_code=404,
                detail=f"未找到工地分组: {camera.group_id}"
            )
            
        # 检查摄像头ID是否已存在
        existing_camera = await camera_service.get_camera(db, camera.camera_id)
        if existing_camera:
            raise HTTPException(
                status_code=400,
                detail=f"摄像头ID已存在: {camera.camera_id}"
            )
            
        # 创建摄像头
        new_camera = await camera_service.create_camera(db, camera)
        
        # 获取完整信息
        status = await camera_service.get_camera_status(db, new_camera.camera_id)
        
        return {
            "camera_id": new_camera.camera_id,
            "camera_name": new_camera.camera_name,
            "group_id": new_camera.group_id,
            "location": new_camera.location,
            "description": new_camera.description,
            "status": new_camera.status,
            "scenes": [scene.scene_id for scene in new_camera.scenes],
            "active_hazards": status["active_hazards"] if status else 0,
            "created_at": new_camera.created_at,
            "updated_at": new_camera.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建摄像头失败: {str(e)}"
        )

@router.put(
    "/{camera_id}",
    response_model=CameraBase,
    summary="更新摄像头",
    description="更新指定摄像头的信息，包括基本信息和场景关联"
)
async def update_camera(
    camera_id: str = Path(..., description="摄像头ID"),
    camera_update: CameraUpdate = Body(..., description="摄像头更新参数"),
    db: AsyncSession = Depends(get_db)
):
    """
    更新摄像头信息
    
    参数:
    - camera_id: 摄像头ID
    - camera_update: 更新参数
        - camera_name: 摄像头名称（可选）
        - group_id: 所属工地分组ID（可选）
        - location: 安装位置（可选）
        - description: 描述信息（可选）
        - status: 状态（可选）
        - scenes: 关联的场景ID列表（可选）
    
    返回:
    - 更新后的摄像头完整信息
    
    注意:
    - 只需提供需要更新的字段
    - 如果提供scenes，将完全替换现有的场景关联
    - 更新group_id时会验证新工地分组是否存在
    """
    try:
        # 检查摄像头是否存在
        camera = await camera_service.get_camera(db, camera_id)
        if not camera:
            raise HTTPException(
                status_code=404,
                detail=f"未找到摄像头: {camera_id}"
            )
            
        # 如果要更新工地组，检查新的工地组是否存在
        if camera_update.group_id:
            site_group = await camera_service.get_site_group(db, camera_update.group_id)
            if not site_group:
                raise HTTPException(
                    status_code=404,
                    detail=f"未找到工地分组: {camera_update.group_id}"
                )
                
        # 更新摄像头
        updated_camera = await camera_service.update_camera(db, camera_id, camera_update)
        
        # 获取完整信息
        status = await camera_service.get_camera_status(db, updated_camera.camera_id)
        
        return {
            "camera_id": updated_camera.camera_id,
            "camera_name": updated_camera.camera_name,
            "group_id": updated_camera.group_id,
            "location": updated_camera.location,
            "description": updated_camera.description,
            "status": updated_camera.status,
            "scenes": [scene.scene_id for scene in updated_camera.scenes],
            "active_hazards": status["active_hazards"] if status else 0,
            "created_at": updated_camera.created_at,
            "updated_at": updated_camera.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新摄像头失败: {str(e)}"
        )

@router.delete(
    "/{camera_id}",
    summary="删除摄像头",
    description="删除指定的摄像头，同时会删除相关的场景关联和隐患记录"
)
async def delete_camera(
    camera_id: str = Path(..., description="摄像头ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    删除摄像头
    
    参数:
    - camera_id: 摄像头ID
    
    返回:
    - 删除成功的确认信息
    
    注意:
    - 删除操作会同时删除:
        - 摄像头基本信息
        - 场景关联关系
        - 相关的隐患记录
    - 此操作不可恢复
    """
    try:
        # 检查摄像头是否存在
        camera = await camera_service.get_camera(db, camera_id)
        if not camera:
            raise HTTPException(
                status_code=404,
                detail=f"未找到摄像头: {camera_id}"
            )
            
        # 删除摄像头
        await camera_service.delete_camera(db, camera_id)
        
        return {"message": f"摄像头 {camera_id} 删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除摄像头失败: {str(e)}"
        ) 