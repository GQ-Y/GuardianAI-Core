import asyncio
import sys
from pathlib import Path
from datetime import datetime

project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from app.database import AsyncSessionLocal
from app.models import Camera, CameraScene, Hazard, HazardTrack, SiteGroup

async def check_database():
    """检查数据库状态"""
    print("\n=== 数据库状态检查 ===")
    
    async with AsyncSessionLocal() as db:
        # 检查工地分组
        groups = await db.execute("SELECT COUNT(*) FROM site_groups")
        group_count = groups.scalar()
        print(f"\n工地分组数量: {group_count}")
        
        # 检查摄像头
        cameras = await db.execute("SELECT COUNT(*) FROM cameras")
        camera_count = cameras.scalar()
        print(f"摄像头数量: {camera_count}")
        
        # 检查场景关联
        scenes = await db.execute("SELECT COUNT(*) FROM camera_scenes")
        scene_count = scenes.scalar()
        print(f"场景关联数量: {scene_count}")
        
        # 检查隐患记录
        hazards = await db.execute("""
            SELECT status, COUNT(*) 
            FROM hazards 
            GROUP BY status
        """)
        print("\n隐患统计:")
        for status, count in hazards:
            print(f"- {status}: {count}条")
            
        # 检查最近的隐患
        recent_hazards = await db.execute("""
            SELECT h.hazard_id, h.violation_type, h.risk_level, h.status,
                   c.camera_name, h.detected_at
            FROM hazards h
            JOIN cameras c ON h.camera_id = c.camera_id
            ORDER BY h.detected_at DESC
            LIMIT 5
        """)
        print("\n最近5条隐患记录:")
        for h in recent_hazards:
            detected_time = h.detected_at.strftime("%Y-%m-%d %H:%M:%S")
            print(f"- [{h.risk_level}] {h.violation_type}")
            print(f"  摄像头: {h.camera_name}")
            print(f"  状态: {h.status}")
            print(f"  发现时间: {detected_time}")
            print()

if __name__ == "__main__":
    asyncio.run(check_database()) 