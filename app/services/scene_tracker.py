import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)  # 在类外创建logger

class SceneTracker:
    def __init__(self):
        # 在项目数据目录下创建场景状态文件
        self.data_dir = os.path.join(settings.BASE_DIR, 'data')
        if not os.path.exists(self.data_dir):
            logger.info(f"Creating data directory at {self.data_dir}")
            os.makedirs(self.data_dir)
            
        self.data_file = os.path.join(self.data_dir, 'scene_states.json')
        logger.info(f"Initializing SceneTracker with data file: {self.data_file}")
        self.states = self._load_states()
    
    def _load_states(self) -> Dict:
        """加载历史状态数据"""
        try:
            if os.path.exists(self.data_file):
                logger.info(f"Loading scene states from {self.data_file}")
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.info(f"Creating new scene states file at {self.data_file}")
                initial_states = {
                    "scenes": {},
                    "last_update": None
                }
                # 创建新文件
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_states, f, ensure_ascii=False, indent=2)
                return initial_states
                
        except Exception as e:
            logger.error(f"Error loading scene states: {str(e)}")
            return {
                "scenes": {},
                "last_update": None
            }
    
    def _save_states(self):
        """保存状态数据"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # 保存状态
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.states, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Scene states saved to {self.data_file}")
            
        except Exception as e:
            logger.error(f"Error saving scene states: {str(e)}")
            raise
    
    def update_state(self, scene_id: str, new_state: Dict):
        """更新场景状态"""
        try:
            if scene_id not in self.states["scenes"]:
                logger.info(f"Creating new scene record for {scene_id}")
                self.states["scenes"][scene_id] = {
                    "history": [],
                    "current": None
                }
            
            # 将当前状态移入历史记录
            if self.states["scenes"][scene_id]["current"]:
                self.states["scenes"][scene_id]["history"].append(
                    self.states["scenes"][scene_id]["current"]
                )
                # 保留最近15条记录
                if len(self.states["scenes"][scene_id]["history"]) > 15:
                    self.states["scenes"][scene_id]["history"].pop(0)
            
            # 更新当前状态
            new_state["timestamp"] = datetime.now().isoformat()
            self.states["scenes"][scene_id]["current"] = new_state
            self.states["last_update"] = datetime.now().isoformat()
            
            # 保存状态
            self._save_states()
            
            logger.info(f"Updated state for scene {scene_id}")
            
        except Exception as e:
            logger.error(f"Error updating scene state: {str(e)}")
            raise
    
    def get_scene_history(self, scene_id: str, count: int = 15) -> List[Dict]:
        """获取场景历史状态"""
        try:
            if scene_id not in self.states["scenes"]:
                logger.info(f"No history found for scene {scene_id}")
                return []
                
            history = self.states["scenes"][scene_id]["history"]
            current = self.states["scenes"][scene_id]["current"]
            
            if current:
                history = history + [current]
            
            return history[-count:]
            
        except Exception as e:
            logger.error(f"Error getting scene history: {str(e)}")
            return []
            
    def get_scene_info(self, scene_id: str) -> Optional[Dict]:
        """获取场景信息"""
        try:
            if scene_id in self.states["scenes"]:
                scene = self.states["scenes"][scene_id]
                return {
                    "scene_id": scene_id,
                    "history_count": len(scene["history"]),
                    "has_current": scene["current"] is not None,
                    "last_update": scene["current"]["timestamp"] if scene["current"] else None
                }
            logger.info(f"No scene info found for {scene_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting scene info: {str(e)}")
            return None