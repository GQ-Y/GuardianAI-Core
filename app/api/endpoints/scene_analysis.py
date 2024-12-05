from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict
import base64

from ...services.scene_analysis_service import SceneAnalysisService

router = APIRouter(
    prefix="/analysis",
    tags=["scene-analysis"],
    responses={404: {"description": "Not found"}},
)

scene_analysis = SceneAnalysisService()

@router.post("/{scene_id}", 
    summary="分析场景状态",
    description="""
    分析施工现场图片，跟踪挖掘机和人员状态。
    
    功能：
    - 跟踪挖掘机位置和工作状态
    - 识别周边人员情况
    - 评估施工安全状况
    
    返回：
    - 挖掘机状态信息
    - 人员分布情况
    - 安全评估结果
    """
)
async def analyze_scene(
    scene_id: str,
    file: UploadFile = File(..., description="施工现场图片文件")
) -> Dict:
    """
    分析场景状态
    
    Parameters:
    - scene_id: 场景ID，用于关联历史记录
    - file: 图片文件，支持jpg/png格式
    
    Returns:
    - 分析结果，包含挖掘机状态、人员情况和安全评估
    """
    try:
        # 验证文件格式
        if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise HTTPException(
                status_code=400,
                detail="只支持jpg/png格式的图片"
            )
            
        # 读取并编码图片
        content = await file.read()
        image_base64 = base64.b64encode(content).decode()
        
        # 分析场景
        result = await scene_analysis.analyze_frame(scene_id, image_base64)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        ) 