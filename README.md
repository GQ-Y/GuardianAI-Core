# 建筑工地安全监控系统

本系统用于实时监控建筑工地的安全隐患，通过AI分析摄像头图片来识别潜在的安全问题。

## 目录结构

```
secure/
├── alembic/                # 数据库迁移文件
├── app/                    # 主应用代码
│   ├── api/               # API接口
│   ├── models/            # 数据库模型
│   ├── schemas/           # 数据验证模型
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具函数
├── scripts/               # 管理脚本
├── uploads/               # 图片上传目录
├── logs/                  # 日志目录
└── tests/                 # 测试代码
```

## 环境要求

- Python 3.9+
- SQLite 3
- 智谱AI API密钥

## 环境初始化

1. 创建虚拟环境：
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
# 编辑.env文件，填入必要Key等配置信息
```

## 数据库迁移

1. 初始化数据库：
```bash
alembic upgrade head
```

2. 创建新的迁移：
```bash
alembic revision -m "migration_name"
```

3. 回滚迁移：
```bash
alembic downgrade -1  # 回滚一个版本
alembic downgrade base  # 回滚到初始状态
```

## 测试数据初始化

1. 运行初始化脚本：
```bash
python scripts/init_test_data.py
```

这将创建：
- 示例工地分组
- 测试摄像头
- 场景关联关系

## 启动服务

```bash
python run.py
```

服务将在 http://localhost:8000 启动，API文档在 http://localhost:8000/docs

## API接口说明

### 工地分组管理

#### 获取工地分组列表
```http
GET /api/v1/site/groups
```

返回：工地分组列表
```json
[
    {
        "group_id": "site_001",
        "group_name": "北京地铁13号线",
        "description": "13号线施工现场",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
]
```

#### 创建工地分组
```http
POST /api/v1/site/groups
```

请求体：
```json
{
    "group_id": "site_002",
    "group_name": "北京地铁14号线",
    "description": "14号线施工现场"
}
```

#### 更新工地分组
```http
PUT /api/v1/site/groups/{group_id}
```

请求体：
```json
{
    "group_name": "新的分组名称",
    "description": "更新的描述"
}
```

#### 删除工地分组
```http
DELETE /api/v1/site/groups/{group_id}
```

### 摄像头管理

#### 获取摄像头列表
```http
GET /api/v1/camera/
```

返回：摄像头列表
```json
[
    {
        "camera_id": "cam_001",
        "camera_name": "基坑东侧摄像头",
        "group_id": "site_001",
        "location": "基坑东侧10米处",
        "status": "active",
        "scenes": ["excavation_edge_protection"],
        "active_hazards": 2
    }
]
```

#### 创建摄像头
```http
POST /api/v1/camera/
```

请求体：
```json
{
    "camera_id": "cam_002",
    "camera_name": "材料区摄像头",
    "group_id": "site_001",
    "location": "材料堆放区",
    "scenes": ["material_storage"]
}
```

#### 更新摄像头
```http
PUT /api/v1/camera/{camera_id}
```

请求体：
```json
{
    "camera_name": "新的摄像头名称",
    "location": "新的位置",
    "scenes": ["新的场景ID"]
}
```

#### 删除摄像头
```http
DELETE /api/v1/camera/{camera_id}
```

#### 上传图片并分析
```http
POST /api/v1/camera/frame/{camera_id}
```

请求体：
- 使用multipart/form-data格式
- 文件字段名：file
- 支持jpg/png格式

返回：分析结果
```json
{
    "status": "success",
    "result": {
        "existing_hazards": [],
        "new_hazards": [],
        "voice_warnings": []
    }
}
```
