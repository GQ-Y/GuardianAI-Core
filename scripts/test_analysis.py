import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from app.database import AsyncSessionLocal
from app.models import Hazard, HazardTrack

async def check_hazards():
    """检查隐患记录"""
    async with AsyncSessionLocal() as db:
        # 查询所有隐患
        sql = text("""
            SELECT h.*, ht.details 
            FROM hazards h 
            LEFT JOIN hazard_tracks ht ON h.hazard_id = ht.hazard_id
            ORDER BY h.created_at DESC
        """)
        
        result = await db.execute(sql)
        hazards = result.fetchall()
        
        print("\nHazard Records:")
        for hazard in hazards:
            print(f"\nHazard ID: {hazard.hazard_id}")
            print(f"Type: {hazard.violation_type}")
            print(f"Location: {hazard.location}")
            print(f"Risk Level: {hazard.risk_level}")
            print(f"Status: {hazard.status}")
            print(f"Details: {hazard.details}")

        # 使用ORM方式再次查询（可选）
        print("\nUsing ORM Query:")
        from sqlalchemy import select
        stmt = select(Hazard).order_by(Hazard.created_at.desc())
        result = await db.execute(stmt)
        hazards = result.scalars().all()
        
        for hazard in hazards:
            print(f"\nHazard ID: {hazard.hazard_id}")
            print(f"Camera ID: {hazard.camera_id}")
            print(f"Scene ID: {hazard.scene_id}")
            print(f"Type: {hazard.violation_type}")
            print(f"Location: {hazard.location}")
            print(f"Risk Level: {hazard.risk_level}")
            print(f"Status: {hazard.status}")
            
            # 获取最新的跟踪记录
            track_stmt = select(HazardTrack).where(
                HazardTrack.hazard_id == hazard.hazard_id
            ).order_by(HazardTrack.created_at.desc())
            track_result = await db.execute(track_stmt)
            latest_track = track_result.scalar_one_or_none()
            
            if latest_track:
                print(f"Latest Track Details: {latest_track.details}")

if __name__ == "__main__":
    asyncio.run(check_hazards()) 