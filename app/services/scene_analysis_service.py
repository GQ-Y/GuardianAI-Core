import json
from typing import Dict, List
import logging
from .ai_clients.stepai_client import StepAIClient
from .scene_tracker import SceneTracker

logger = logging.getLogger(__name__)

class SceneAnalysisService:
    def __init__(self):
        self.ai_client = StepAIClient()
        self.tracker = SceneTracker()
        
    def _build_analysis_prompt(self, scene_id: str, history_states: List[Dict]) -> str:
        """构建分析提示词"""
        prompt = f"""你是一位专业的施工现场安全检查员，请分析这张施工现场图片，重点关注以下内容：

1. 机械设备检测：

1.1 吊车检测：
- 判断画面中是否存在吊车
- 给出判断的置信度(0-1之间的数值)
- 重点观察起重臂状态和方向：
  · 状态：展开/收起
  · 方向：水平/倾斜/垂直（相对于地面）
- 注意：起重臂状态和方向是判断工作状态的主要依据

2. 如果存在吊车，请详细分析：
- 位置：相对于场地的具体位置（需要具体到方位和参照物）
- 特征：型号、颜色
- 工作状态判断标准（综合考虑以下因素）：
  · 主要依据：起重臂状态和方向
    - working: 起重臂完全展开且呈倾斜或垂直状态
    - idle: 以下任一情况：
      1. 起重臂处于收起状态
      2. 起重臂虽展开但保持水平方向（未进入工作角度）
      3. 起重臂部分收起
    - absent: 吊车不在画面中
  · 辅助判断：与历史状态对比
    - 位置变化：记录吊车位置是否发生移动
    - 起重臂方向：记录起重臂方向是否发生改变
    - 作业连续性：如果上一状态为working，且位置或起重臂方向有变化，说明正在持续作业
- 如果判定为idle状态，则无需进行后续分析

3. 人员情况：
- 仅在吊车处于working状态时分析
- 统计吊车4米范围内的人员数量
- 重点识别戴红色和白色安全帽的管理人员
- 记录每个人员的：
  · 位置（相对于吊车的方位和距离）
  · 安全帽颜色（红色与白色均为管理人员，黄色为工人，其他颜色记录具体颜色）
  · 角色判定（基于安全帽颜色）
  · 行为状态（站立、走动、指挥等）

4. 状态变化分析：
请对比历史记录，分析以下变化：
- 吊车位置变化：具体描述移动方向和距离
- 起重臂状态和方向变化：
  · 描述起重臂角度变化（水平/倾斜/垂直）
  · 描述展开程度的变化
- 人员数量变化：说明人员的增减情况
- 作业连续性判断：根据位置和起重臂变化判断是否属于同一作业过程

历史状态记录（从新到旧）：
"""
        
        # 添加历史状态信息时进行防御性检查
        if history_states and isinstance(history_states, list):
            for state in history_states:
                if not isinstance(state, dict):
                    continue
                    
                # 使用多层get并提供默认值
                crane_data = state.get('crane', {})
                features = crane_data.get('features', {})
                
                prompt += f"""
时间：{state.get('timestamp', 'unknown')}
吊车状态：
- 位置：{crane_data.get('position', 'unknown')}
- 起重臂状态：{features.get('boom_state', 'unknown')}
- 工作状态：{crane_data.get('status', 'unknown')}
人员情况：{len(state.get('personnel', []))}人
"""
        
        prompt += """
请用JSON格式返回分析结果，格式如下：
{
    "crane": {
        "presence": true|false,
        "position": "具体位置描述|null当不存在时",
        "features": {
            "model": "型号",
            "color": "颜色",
            "boom_state": "展开|收起",
            "boom_direction": "水平|倾斜|垂直",
            "boom_angle": "相对于地面的大致角度（度）"
        }|null当不存在时,
        "status": "working|idle|absent",
        "confidence": 0.95,
        "movement": {
            "position_changed": true|false,
            "movement_description": "位置变化描述",
            "boom_changed": true|false,
            "boom_change_description": "起重臂状态和方向变化描述"
        }
    },
    "personnel": [
        {
            "position": "相对位置描述",
            "helmet_color": "安全帽颜色",
            "role": "worker|manager",
            "behavior": "行为描述",
            "distance_to_crane": "数值或描述"
        }
    ],
    "safety_status": {
        "has_supervisor": true|false,
        "has_crane_supervisor": true|false,
        "risk_level": "high|medium|low",
        "issues": ["存在的问题"]
    },
    "state_analysis": {
        "continuous_operation": true|false,
        "operation_description": "作业连续性分析描述",
        "personnel_changes": "人员变化描述"
    }
}

注意事项：
1. 必须首先判断机械设备是否存在，并给出置信度
2. 当设备不存在时，相关字段设为null
3. 工作状态判断需要综合考虑起重臂状态、方向和历史变化
4. 起重臂处于水平方向时，即使展开也应判定为idle状态
5. 吊车作业时必须有戴红色或白色安全帽的管理人员在场，否则记录为无人旁站问题
6. 状态变化描述必须准确反映实际情况
7. 所有判断都应该基于当前画面的实际观察，并结合历史数据进行综合分析
"""
        return prompt
    
    async def analyze_frame(self, scene_id: str, image_base64: str) -> Dict:
        """分析单帧图片"""
        try:
            # 获取历史状态并确保返回列表
            history_states = self.tracker.get_scene_history(scene_id) or []
            
            # 验证历史状态格式
            if not isinstance(history_states, list):
                history_states = []
                logger.warning(f"Invalid history states format for scene {scene_id}")
            
            # 构建提示词
            prompt = self._build_analysis_prompt(scene_id, history_states)
            
            # 调用AI分析
            result_text = await self.ai_client.analyze_image(image_base64, prompt)
            
            # 解析JSON结果
            try:
                # 提取JSON部分
                if "```json" in result_text:
                    start = result_text.find("```json\n") + 8
                    end = result_text.find("```", start)
                    json_str = result_text[start:end].strip()
                else:
                    json_str = result_text.strip()
                
                result = json.loads(json_str)
                
                # 更新状态记录
                self.tracker.update_state(scene_id, result)
                
                return {
                    "status": "success",
                    "scene_id": scene_id,
                    "result": result
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}\nText: {result_text}")
                return {
                    "status": "error",
                    "message": f"Invalid JSON format: {str(e)}"
                }
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
