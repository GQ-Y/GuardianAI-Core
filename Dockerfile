FROM python:3.9

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY alembic.ini .
COPY changjing.json .
COPY scripts/ ./scripts/
COPY alembic/ ./alembic/
COPY app/ ./app/
COPY run.py .

# 创建必要的目录
RUN mkdir -p uploads logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["sh", "-c", "alembic upgrade head && python scripts/init_db.py && python run.py"]