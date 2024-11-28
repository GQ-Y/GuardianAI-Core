from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class CameraScene(BaseModel):
    """摄像头场景关联模型"""
    __tablename__ = 'camera_scenes'
    
    camera_id = Column(String(50), ForeignKey('cameras.camera_id'), nullable=False)
    scene_id = Column(String(50), nullable=False)
    
    # 关系
    camera = relationship("Camera", back_populates="scenes") 