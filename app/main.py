from fastapi import FastAPI
from .api.routes import api_router

app = FastAPI(
    title="Construction Site Safety Monitor",
    description="智能施工现场安全监控系统",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1") 