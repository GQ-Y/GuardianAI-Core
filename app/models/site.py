from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class SiteGroup(BaseModel):
    """工地分组模型"""
    __tablename__ = 'site_groups'
    
    group_id = Column(String(50), unique=True, nullable=False)
    group_name = Column(String(100), nullable=False)
    description = Column(String(500))
    
    # 关系
    cameras = relationship("Camera", back_populates="group")

class Camera(BaseModel):
    """摄像头模型"""
    __tablename__ = 'cameras'
    
    camera_id = Column(String(50), unique=True, nullable=False)
    camera_name = Column(String(100), nullable=False)
    group_id = Column(String(50), ForeignKey('site_groups.group_id'))
    location = Column(String(200), nullable=False)
    status = Column(String(20), default='active')
    description = Column(String(500))
    
    # 关系
    group = relationship("SiteGroup", back_populates="cameras")
    scenes = relationship("CameraScene", back_populates="camera", lazy="joined")
    hazards = relationship("Hazard", back_populates="camera", lazy="joined") 