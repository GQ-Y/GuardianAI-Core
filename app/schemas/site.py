from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class SiteGroupBase(BaseModel):
    """工地分组基础模型"""
    group_id: str = Field(..., description="工地分组ID，例如: site_001")
    group_name: str = Field(..., description="工地分组名称，例如: 北京地铁13号线")
    description: Optional[str] = Field(None, description="工地分组描述信息")

class SiteGroupCreate(SiteGroupBase):
    """创建工地分组请求模型"""
    pass

class SiteGroupUpdate(BaseModel):
    """更新工地分组请求模型"""
    group_name: Optional[str] = Field(None, description="工地分组名称")
    description: Optional[str] = Field(None, description="工地分组描述信息")

class SiteGroupInfo(SiteGroupBase):
    """工地分组信息响应模型"""
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")

    class Config:
        from_attributes = True

class SiteGroupDetail(SiteGroupInfo):
    """工地分组详细信息响应模型"""
    cameras: List[dict] = Field(..., description="关联的摄像头列表")

class CameraBase(BaseModel):
    """摄像头基础模型"""
    camera_id: str = Field(..., description="摄像头ID，例如: cam_001")
    camera_name: str = Field(..., description="摄像头名称，例如: 基坑东侧摄像头")
    group_id: str = Field(..., description="所属工地分组ID")
    location: str = Field(..., description="安装位置，例如: 基坑东侧10米处")
    description: Optional[str] = Field(None, description="摄像头描述信息")
    status: str = Field("active", description="摄像头状态：active-正常, inactive-停用")

class CameraCreate(CameraBase):
    """创建摄像头请求模型"""
    scenes: List[str] = Field([], description="关联的场景ID列表，例如: ['excavation_edge_protection']")

class CameraUpdate(BaseModel):
    """更新摄像头请求模型"""
    camera_name: Optional[str] = Field(None, description="摄像头名称")
    group_id: Optional[str] = Field(None, description="所属工地分组ID")
    location: Optional[str] = Field(None, description="安装位置")
    description: Optional[str] = Field(None, description="摄像头描述信息")
    status: Optional[str] = Field(None, description="摄像头状态")
    scenes: Optional[List[str]] = Field(None, description="关联的场景ID列表")