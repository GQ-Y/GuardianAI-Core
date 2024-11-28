#!/bin/bash

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
alembic upgrade head

# 初始化测试数据
python scripts/init_db.py 