import uvicorn
from app import create_app
from app.config import settings

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG
    ) 