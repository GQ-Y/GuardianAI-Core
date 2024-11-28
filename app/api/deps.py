from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..config import settings

async def get_db_session() -> Generator:
    """获取数据库会话"""
    try:
        db = await get_db()
        yield db
    finally:
        await db.close()

async def verify_api_key(api_key: str = Depends(get_api_key)):
    """验证API密钥"""
    if api_key != settings.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        ) 