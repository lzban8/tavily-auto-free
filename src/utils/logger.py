"""
日志工具模块

这个模块提供了日志记录功能，主要包括：
- 日志记录器的配置和初始化
- 日志文件的创建和管理
- 日志格式的定义
- 多重输出（控制台和文件）

使用 Python 标准库的 logging 模块实现，支持灵活的日志记录和管理。
"""

import os
import sys
import logging
from datetime import datetime

def setup_logger():
    """
    设置日志记录器
    
    配置日志记录器，包括：
    - 创建日志目录
    - 设置日志文件名
    - 配置日志格式
    - 设置输出处理器
    
    Returns:
        Logger: 配置好的日志记录器实例
    """
    # 创建 logs 目录（如果不存在）
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 设置日志文件名（使用当前时间）
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"tavily_auto_{current_time}.log")

    # 配置日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)

# 初始化日志记录器
logger = setup_logger()

# 设置日志格式
log_format = '%(asctime)s - %(levelname)s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为 INFO
    format=log_format,   # 使用预定义的日志格式
    datefmt=date_format, # 使用预定义的日期格式
    handlers=[
        # 控制台输出处理器
        logging.StreamHandler(sys.stdout),
        # 文件输出处理器
        logging.FileHandler(
            filename=f'logs/tavily_auto_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            encoding='utf-8'
        )
    ]
) 
