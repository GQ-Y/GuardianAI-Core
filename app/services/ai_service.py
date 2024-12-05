from sqlalchemy.ext.asyncio import AsyncSession
import base64
import json
from typing import Optional, Dict, List
import uuid
from datetime import datetime
import os
from PIL import Image
import io
import logging
from app.utils.logger import setup_logger

from ..models.site import Camera
from ..models.hazard import Hazard, HazardTrack
from .ai_clients.zhipu_client import ZhipuAIClient
from .ai_clients.stepai_client import StepAIClient
from ..config import settings

# 初始化logger
logger = setup_logger('ai_service')

class AIService:
    def __init__(self):
        # 根据配置选择AI客户端
        if settings.STEPAI_API_KEY:
            self.ai_client = StepAIClient()
        else:
            self.ai_client = ZhipuAIClient()
    
    async def analyze_image(
        self,
        db: AsyncSession,
        camera: Camera,
        image_path: str
    ) -> dict:
        """分析图片并识别隐患"""
        try:
            # 1. 读取并处理图片
            with Image.open(image_path) as img:
                # 转换为RGB模式
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # 调整图片大小，如果太大的话
                max_size = (1024, 1024)  # 设置最大尺寸
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # 保存为JPEG格式（通常比PNG小）
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=85)
                img_byte_arr = img_byte_arr.getvalue()
                image_data = base64.b64encode(img_byte_arr).decode()
                
                logger.info(f"处理后的图片大小: {len(image_data)} bytes")
                
            # 2. 获取摄像头关联的场景
            scenes = [scene.scene_id for scene in camera.scenes]
            
            # 3. 获取当前活跃的隐患
            active_hazards = [
                hazard for hazard in camera.hazards 
                if hazard.status == 'active'
            ]
            
            # 4. 构建AI提示词
            prompt = build_analysis_prompt(camera, scenes, active_hazards)
            
            # 记录完整提示词到日志
            logger.info("=" * 50)
            logger.info("分析开始时间: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            logger.info("摄像头ID: %s", camera.camera_id)
            logger.info("摄像头位置: %s", camera.location)
            logger.info("关联场景: %s", ", ".join(scenes))
            logger.info("活跃隐患数: %d", len(active_hazards))
            logger.info("-" * 50)
            logger.info("完整提示词:")
            logger.info(prompt)
            logger.info("-" * 50)
            
            try:
                # 5. 调用AI服务进行分析
                analysis_text = await self.ai_client.analyze_image(image_data, prompt)
                
                # 记录AI响应结果
                logger.info("AI响应结果:")
                logger.info(analysis_text)
                logger.info("=" * 50)
                
                # 6. 处理分析结果
                result = await process_analysis_result(db, camera, analysis_text)
                
                return {
                    "status": "success",
                    "result": result,
                    "image_path": image_path
                }
                
            except Exception as e:
                logger.error("AI分析失败: %s", str(e))
                return {
                    "status": "error",
                    "message": f"AI分析失败: {str(e)}",
                    "image_path": image_path
                }
            
        except Exception as e:
            logger.error("图片处理失败: %s", str(e))
            return {
                "status": "error",
                "message": str(e)
            }

def load_scene_rules() -> Dict:
    """加载场景规则定义"""
    try:
        with open("changjing.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载场景规则失败: {str(e)}")
        return {"construction_scenes": []}

def build_analysis_prompt(
    camera: Camera,
    scenes: list,
    active_hazards: list
) -> str:
    """构建AI分析提示词"""
    # 1. 加载场景规则
    scene_rules = load_scene_rules()
    
    # 2. 获取当前摄像头关注的场景规则
    monitored_scenes = [
        scene for scene in scene_rules["construction_scenes"]
        if scene["id"] in scenes
    ]
    
    # 3. 构建提示词
    prompt = f"""你是一位专业的建筑工地安全检查员，正在通过摄像头 {camera.camera_name}（位于{camera.location}）监控施工现场。请注意：
1. 仔细观察图片细节，避免误判
2. 每个违规情况只报告一次，避免重复
3. 使用具体的方位和距离描述位置（如：距离基坑东南角5米处）
4. 提供详细可执行的整改方案
5. 只报告有明确图片证据的违规行为

需要检查的安全场景和标准如下：
"""
    
    # 添加场景规则
    for scene in monitored_scenes:
        prompt += f"""
场景：{scene['name']}
关键词：{', '.join(scene['keywords'])}
检查标准："""
        
        for condition in scene['conditions']:
            prompt += f"""
- {condition['type']}要求：
  {', '.join(condition['items'])}
  判定标准："""
            if 'standards' in condition:
                for standard in condition['standards']:
                    prompt += f"""
    · {standard['item']}: {standard['criteria']}
    · 违规表现: {', '.join(standard['violation_cases'])}"""
                    
        prompt += f"""
风险等级：{scene['risk_level']}
违规类型：{scene['violation_type']}
相关规范：{scene['regulations']}

"""

    # 添加当前活跃隐患信息
    if active_hazards:
        prompt += "\n当前存在的隐患：\n"
        for hazard in active_hazards:
            prompt += f"""- 隐患ID：{hazard.hazard_id}
  类型：{hazard.violation_type}
  位置：{hazard.location}
  风险等级：{hazard.risk_level}
  
"""

    # 添加分析要求
    prompt += """
请仔细分析图片并：
1. 对每个监控场景：
   - 仔细观察是否存在违规行为
   - 确保有明确的图片证据
   - 准确描述违规位置（使用具体的方位和距离）
   - 按标准评估风险等级

2. 对已存在的隐患：
   - 验证是否仍然存在
   - 详细描述当前状态
   - 提供具体可执行的整改方案，包括：
     · 立即整改措施（责任人、完成时限）
     · 长期解决方案（实施步骤、验收标准）

3. 对新发现的隐患：
   - 确保有明确的图片证据
   - 精确描述违规位置和情况
   - 提供详细的整改建议，包括：
     · 紧急处置措施
     · 系统性解决方案
     · 防止复发的管理建议

4. 生成语音警告：
   - 针对高风险违规优先警告
   - 包含具体的位置和违规描述
   - 提供明确的整改要求和时限

请按以下JSON格式提供分析结果：
{
    "existing_hazards": [
        {
            "hazard_id": "string",
            "status": "active|resolved",
            "current_state": "详细描述当前状态",
            "recommendation": {
                "immediate_action": {
                    "action": "立即采取的措施",
                    "responsible": "责任人",
                    "deadline": "完成时限"
                },
                "long_term_solution": {
                    "solution": "长期解决方案",
                    "steps": ["具体实施步骤"],
                    "criteria": "验收标准"
                }
            }
        }
    ],
    "new_hazards": [
        {
            "scene_id": "string",
            "violation_type": "违规类型",
            "location": "具体位置描述（包含方位和距离）",
            "risk_level": "high|medium|low",
            "evidence": "图片中的具体违规证据描述",
            "description": "详细的违规描述",
            "regulation_reference": "违反的具体规范条款",
            "recommendation": {
                "immediate_action": {
                    "action": "立即采取的措施",
                    "responsible": "责任人",
                    "deadline": "完成时限"
                },
                "long_term_solution": {
                    "solution": "长期解决方案",
                    "steps": ["具体实施步骤"],
                    "criteria": "验收标准"
                }
            }
        }
    ],
    "voice_warnings": [
        {
            "target": "hazard_id或new",
            "message": "警告内容（包含位置、违规描述和整改要求）",
            "urgency": "high|medium|low"
        }
    ]
}

注意事项：
1. 位置描述必须包含具体的方位和距离信息
2. 整改建议必须明确责任人和完成时限
3. 避免重复报告相同的违规情况
4. 确保每个识别的违规都有确切的图片证据
5. 优先关注可能导致重大安全事故的隐患
6. 所有描述和建议必须使用中文
7. 提供的整改措施必须具体可执行
8. 验收标准必须可量化、可检查
"""

    return prompt

async def process_analysis_result(
    db: AsyncSession,
    camera: Camera,
    analysis_text: str
) -> Dict:
    """处理AI分析结果"""
    try:
        # 1. 从返回的文本中提取JSON部分
        json_str = analysis_text
        if "```json" in analysis_text:
            # 如果返回的是markdown格式的JSON，提取JSON部分
            start = analysis_text.find("```json\n") + 8
            end = analysis_text.find("```", start)
            json_str = analysis_text[start:end].strip()
        
        # 2. 解析JSON结果
        result = json.loads(json_str)
        print(f"Parsed analysis result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 3. 更新现有隐患状态
        updated_hazards = []
        for hazard_update in result.get('existing_hazards', []):
            hazard = await update_hazard_status(
                db,
                hazard_update['hazard_id'],
                hazard_update['status'],
                hazard_update['current_state'],
                hazard_update.get('recommendation', '')  # 添加建议字段
            )
            if hazard:
                updated_hazards.append(hazard)
        
        # 4. 创建新的隐患记录
        new_hazards = []
        for new_hazard in result.get('new_hazards', []):
            hazard = await create_new_hazard(
                db,
                camera.camera_id,
                new_hazard
            )
            new_hazards.append(hazard)
        
        # 5. 处理语音警告
        voice_warnings = result.get('voice_warnings', [])
        
        return {
            "status": "success",
            "result": {
                "updated_hazards": [h.hazard_id for h in updated_hazards],
                "new_hazards": [h.hazard_id for h in new_hazards],
                "voice_warnings": voice_warnings
            }
        }
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}\nText: {analysis_text}")
        return {
            "status": "error",
            "message": f"Invalid JSON format: {str(e)}"
        }
    except Exception as e:
        print(f"Processing error: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

async def update_hazard_status(
    db: AsyncSession,
    hazard_id: str,
    status: str,
    current_state: str,
    recommendation: str = ""
) -> Optional[Hazard]:
    """更新隐患状态"""
    hazard = await db.get(Hazard, hazard_id)
    if not hazard:
        return None
        
    # 更新状态
    hazard.status = status
    if status == 'resolved':
        hazard.resolved_at = datetime.utcnow()
        
    # 创建跟踪记录
    track = HazardTrack(
        hazard_id=hazard_id,
        status=status,
        details=f"Current State: {current_state}\nRecommendation: {recommendation}"
    )
    db.add(track)
    
    await db.commit()
    return hazard

async def create_new_hazard(
    db: AsyncSession,
    camera_id: str,
    hazard_data: Dict
) -> Hazard:
    """创建新的隐患记录"""
    # 创建隐患记录
    hazard = Hazard(
        hazard_id=str(uuid.uuid4()),
        camera_id=camera_id,
        scene_id=hazard_data['scene_id'],
        violation_type=hazard_data['violation_type'],
        location=hazard_data['location'],
        risk_level=hazard_data['risk_level'],
        status='active',
        detected_at=datetime.utcnow()
    )
    
    db.add(hazard)
    await db.flush()  # 获取hazard_id
    
    # 创建初始跟踪记录
    track = HazardTrack(
        hazard_id=hazard.hazard_id,
        status='active',
        details=f"""Description: {hazard_data['description']}
Regulation: {hazard_data.get('regulation_reference', 'N/A')}
Location: {hazard_data['location']}
Risk Level: {hazard_data['risk_level']}"""
    )
    db.add(track)
    
    await db.commit()
    return hazard