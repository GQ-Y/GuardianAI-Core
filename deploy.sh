#!/bin/bash

# 创建目录结构
mkdir -p uploads logs
touch safety.db

# 创建.env文件（如果不存在）
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DEBUG=false
DATABASE_URL=sqlite+aiosqlite:///./safety.db
ZHIPU_API_KEY=your-api-key
EOF
    echo "Please edit .env file and set your actual API key"
fi

# 拉取最新镜像
docker pull registry.cn-hangzhou.aliyuncs.com/hook-docker/secure-web:latest

# 启动服务
docker-compose -f docker-compose.deploy.yml up -d

# 显示服务状态
docker-compose -f docker-compose.deploy.yml ps

echo "Service is running at http://localhost:8000"
echo "API documentation is available at http://localhost:8000/docs" 