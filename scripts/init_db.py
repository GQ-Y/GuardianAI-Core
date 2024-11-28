import asyncio
import json
import os
import sys
from pathlib import Path
from sqlalchemy import text, select

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models import SiteGroup, Camera, CameraScene
from app.utils.scene_manager import scene_manager
from app.utils.logger import app_logger

async def validate_scenes():
    """验证场景规则配置"""
    try:
        # 验证场景规则文件
        if not scene_manager.rules:
            raise Exception("Failed to load scene rules")
            
        print(f"Loaded {len(scene_manager.rules.construction_scenes)} scenes")
        
        # 验证每个场景的配置
        for scene in scene_manager.rules.construction_scenes:
            print(f"Validating scene: {scene.id} - {scene.name}")
            
            # 验证关键词
            if not scene.keywords:
                raise Exception(f"Scene {scene.id} has no keywords")
                
            # 验证条件
            if not scene.conditions:
                raise Exception(f"Scene {scene.id} has no conditions")
                
            # 验证风险等级 - 支持中文和英文
            valid_risk_levels = ['high', 'medium', 'low', '高', '中', '低']
            if scene.risk_level not in valid_risk_levels:
                raise Exception(f"Scene {scene.id} has invalid risk level: {scene.risk_level}")
            
            print(f"Scene {scene.id} validated successfully")
                
        return True
        
    except Exception as e:
        print(f"Scene validation failed: {str(e)}")
        return False

async def init_test_data():
    """初始化测试数据"""
    try:
        print("Starting database initialization...")
        
        # 首先验证场景规则
        print("Validating scene rules...")
        if not await validate_scenes():
            print("Scene validation failed, aborting initialization")
            return

        async with AsyncSessionLocal() as db:
            try:
                # 1. 检查是否已存在
                result = await db.execute(text("SELECT COUNT(*) FROM site_groups"))
                count = result.scalar()
                print(f"Found {count} existing site groups")
                
                if count > 0:
                    print("Database already initialized")
                    return

                print("Creating test data...")
                
                # 2. 创建测试工地
                site_group = SiteGroup(
                    group_id="site_001",
                    group_name="测试工地1",
                    description="用于测试的工地"
                )
                db.add(site_group)
                await db.flush()
                print(f"Created site group: {site_group.group_id}")

                # 3. 创建测试摄像头
                camera = Camera(
                    camera_id="cam_001",
                    camera_name="基坑东侧摄像头",
                    group_id=site_group.group_id,
                    location="基坑东侧",
                    description="监控基坑施工区域"
                )
                db.add(camera)
                await db.flush()
                print(f"Created camera: {camera.camera_id}")

                # 4. 关联监控场景
                scenes = ["excavation_edge_protection", "excavation_material_storage"]
                for scene_id in scenes:
                    print(f"Checking scene: {scene_id}")
                    scene_info = scene_manager.get_scene(scene_id)
                    if not scene_info:
                        print(f"Warning: Scene not found: {scene_id}")
                        continue

                    scene = CameraScene(
                        camera_id=camera.camera_id,
                        scene_id=scene_id
                    )
                    db.add(scene)
                    print(f"Created scene association: {scene_id}")

                print("Committing changes...")
                await db.commit()
                print("Test data initialized successfully")

            except Exception as e:
                await db.rollback()
                print(f"Database error: {str(e)}")
                raise

    except Exception as e:
        print(f"Initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        print("Starting initialization process...")
        asyncio.run(init_test_data())
        print("Initialization completed")
    except Exception as e:
        print(f"Failed to initialize database: {str(e)}") 