from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class HazardBase(BaseModel):
    hazard_id: str
    camera_id: str
    scene_id: str
    location: Optional[str] = None
    violation_type: str
    risk_level: str
    status: str = "active"

class HazardCreate(HazardBase):
    pass

class HazardUpdate(HazardBase):
    hazard_id: Optional[str] = None
    status: Optional[str] = None
    resolved_at: Optional[datetime] = None

class Hazard(HazardBase):
    id: int
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class HazardTrackBase(BaseModel):
    hazard_id: str
    status: str
    details: Optional[str] = None

class HazardTrackCreate(HazardTrackBase):
    pass

class HazardTrack(HazardTrackBase):
    id: int
    tracked_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AnalysisResult(BaseModel):
    status: str
    message: Optional[str] = None
    result: Optional[dict] = None

class CameraInfo(BaseModel):
    """摄像头信息"""
    camera_id: str
    camera_name: str
    group_id: str
    location: str
    description: Optional[str] = None
    status: str
    scenes: List[str]
    active_hazards: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CameraCreate(BaseModel):
    """创建摄像头请求模型"""
    camera_id: str
    camera_name: str
    group_id: str
    location: str
    description: Optional[str] = None
    status: str = "active"
    scenes: List[str] = []

class CameraUpdate(BaseModel):
    """更新摄像头请求模型"""
    camera_name: Optional[str] = None
    group_id: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    scenes: Optional[List[str]] = None 