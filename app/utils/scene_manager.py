import json
import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import jsonschema

class SceneCondition(BaseModel):
    type: str
    items: List[str]

class Scene(BaseModel):
    id: str
    name: str
    keywords: List[str]
    conditions: List[SceneCondition]
    risk_level: str
    violation_type: str
    regulations: str

class SceneRules(BaseModel):
    construction_scenes: List[Scene]

class SceneManager:
    def __init__(self, rules_file: str = "changjing.json"):
        self.rules_file = rules_file
        self.rules: Optional[SceneRules] = None
        self._load_rules()

    def _load_rules(self) -> None:
        """加载场景规则"""
        try:
            if not os.path.exists(self.rules_file):
                raise FileNotFoundError(f"Rules file not found: {self.rules_file}")
                
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.rules = SceneRules(**data)
                
        except Exception as e:
            raise Exception(f"Failed to load scene rules: {str(e)}")

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """获取指定场景规则"""
        if not self.rules:
            return None
            
        for scene in self.rules.construction_scenes:
            if scene.id == scene_id:
                return scene
        return None

    def get_scenes_by_keywords(self, keywords: List[str]) -> List[Scene]:
        """根据关键词查找场景"""
        if not self.rules:
            return []
            
        matched_scenes = []
        for scene in self.rules.construction_scenes:
            if any(keyword in scene.keywords for keyword in keywords):
                matched_scenes.append(scene)
        return matched_scenes

    def validate_scene_conditions(self, scene_id: str, conditions: Dict) -> bool:
        """验证场景条件是否满足"""
        scene = self.get_scene(scene_id)
        if not scene:
            return False
            
        for condition in scene.conditions:
            if condition.type not in conditions:
                return False
            if not all(item in conditions[condition.type] for item in condition.items):
                return False
        return True

# 创建全局场景管理器实例
scene_manager = SceneManager() 