import logging
import os
from logging.handlers import RotatingFileHandler
from ..config import settings

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    设置logger
    
    Args:
        name: logger名称
        log_file: 日志文件路径(可选)
        
    Returns:
        logging.Logger: 配置好的logger实例
    """
    # 如果未指定日志文件，使用默认路径
    if log_file is None:
        log_file = os.path.join(settings.ensure_log_dir, f'{name}.log')
    
    # 创建logger
    logger = logging.getLogger(name)
    
    # 设置日志级别
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    logger.setLevel(log_level)
    
    # 避免重复添加handler
    if not logger.handlers:
        # 创建文件处理器(支持日志轮转)
        fh = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        fh.setLevel(log_level)
        
        # 创建控制台处理器
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)  # 控制台只显示INFO及以上级别
        
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger 