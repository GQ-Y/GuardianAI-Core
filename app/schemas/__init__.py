from .camera import HazardBase, HazardCreate, HazardUpdate, Hazard, HazardTrackBase, HazardTrackCreate, HazardTrack, AnalysisResult
from .site import (
    SiteGroupBase,
    SiteGroupCreate,
    SiteGroupUpdate,
    SiteGroupInfo,
    SiteGroupDetail,
    CameraBase,
    CameraCreate,
    CameraUpdate
)

__all__ = [
    # Camera and Hazard related schemas
    'HazardBase',
    'HazardCreate',
    'HazardUpdate',
    'Hazard',
    'HazardTrackBase',
    'HazardTrackCreate',
    'HazardTrack',
    'AnalysisResult',
    
    # Site and Camera related schemas
    'SiteGroupBase',
    'SiteGroupCreate',
    'SiteGroupUpdate',
    'SiteGroupInfo',
    'SiteGroupDetail',
    'CameraBase',
    'CameraCreate',
    'CameraUpdate'
] 