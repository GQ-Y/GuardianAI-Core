from .base import Base
from .site import SiteGroup, Camera
from .scene import CameraScene
from .hazard import Hazard, HazardTrack

# 确保所有模型都被导入和注册
__all__ = [
    'Base',
    'SiteGroup',
    'Camera',
    'CameraScene',
    'Hazard',
    'HazardTrack'
] 