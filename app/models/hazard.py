from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime

class Hazard(BaseModel):
    """隐患记录模型"""
    __tablename__ = 'hazards'
    
    hazard_id = Column(String(50), unique=True, nullable=False)
    camera_id = Column(String(50), ForeignKey('cameras.camera_id'), nullable=False)
    scene_id = Column(String(50), nullable=False)
    location = Column(String(200))
    violation_type = Column(String(100), nullable=False)
    risk_level = Column(String(20), nullable=False)
    status = Column(String(20), default='active')
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # 关系
    camera = relationship("Camera", back_populates="hazards")
    tracks = relationship("HazardTrack", back_populates="hazard")

class HazardTrack(BaseModel):
    """隐患跟踪记录模型"""
    __tablename__ = 'hazard_tracks'
    
    hazard_id = Column(String(50), ForeignKey('hazards.hazard_id'), nullable=False)
    status = Column(String(20), nullable=False)
    details = Column(Text)
    tracked_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    hazard = relationship("Hazard", back_populates="tracks") 