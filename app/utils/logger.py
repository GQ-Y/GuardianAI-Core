import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str, log_file: str, level=logging.INFO):
    """配置日志"""
    # 创建日志目录
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 创建处理器
    handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # 设置格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(handler)
    
    return logger

# 创建应用日志
app_logger = setup_logger(
    'app',
    'logs/app.log'
)

# 创建访问日志
access_logger = setup_logger(
    'access',
    'logs/access.log'
) 