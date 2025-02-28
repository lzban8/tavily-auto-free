"""
配置管理模块

这个模块负责管理整个应用的配置信息，主要功能包括：
- 环境变量的加载和管理
- 浏览器配置项的设置
- 注册相关参数的配置
- 邮箱服务的配置
- 配置有效性检查

使用 python-dotenv 实现环境变量的加载和管理，支持灵活的配置修改。
"""

import os
import sys
from dotenv import load_dotenv
from utils.logger import setup_logger

# 初始化日志
logger = setup_logger()

class Config:
    """
    配置管理类
    
    负责管理所有的配置项，包括：
    - 浏览器配置（类型、模式、用户代理等）
    - 注册配置（URL等）
    - 邮箱配置（临时邮箱、IMAP等）
    - 域名配置
    """

    def __init__(self):
        """
        初始化配置管理器
        
        从 .env 文件加载配置，设置默认值，
        并进行配置有效性检查
        """
        # 加载.env文件
        load_dotenv()
        
        # 浏览器配置
        self.BROWSER_TYPE = os.getenv('BROWSER_TYPE', 'chrome')
        self.HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
        self.BROWSER_USER_AGENT = os.getenv('BROWSER_USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        self.BROWSER_WIDTH = int(os.getenv('BROWSER_WIDTH', '1920'))
        self.BROWSER_HEIGHT = int(os.getenv('BROWSER_HEIGHT', '1080'))
        
        # 注册配置
        self.REGISTER_URL = os.getenv('REGISTER_URL', 'https://app.tavily.com/sign-up')
        
        # 临时邮箱配置
        self.TEMP_MAIL = os.getenv('TEMP_MAIL')
        self.TEMP_MAIL_EXT = os.getenv('TEMP_MAIL_EXT', '@mailto.plus')
        self.TEMP_MAIL_EPIN = os.getenv('TEMP_MAIL_EPIN')
        self.TEMP_MAIL_API_URL = os.getenv('TEMP_MAIL_API_URL', 'https://tempmail.plus/api')
        
        # 域名配置
        self.DOMAIN = os.getenv('DOMAIN', '@lzban8.me')
        
        # IMAP配置
        self.IMAP_SERVER = os.getenv('IMAP_SERVER')
        self.IMAP_PORT = int(os.getenv('IMAP_PORT', '993'))
        self.IMAP_USER = os.getenv('IMAP_USER')
        self.IMAP_PASS = os.getenv('IMAP_PASS')
        self.IMAP_DIR = os.getenv('IMAP_DIR', 'INBOX')

        self.check_config()

    def check_config(self):
        """
        检查配置项是否有效
        
        检查必需的配置项是否存在且有效，
        包括浏览器配置和邮箱配置
        
        Raises:
            ValueError: 当必需的配置项缺失或无效时
        """
        required_configs = {
            "BROWSER_TYPE": "浏览器类型",
        }

        for key, name in required_configs.items():
            if not self.check_is_valid(getattr(self, key)):
                raise ValueError(f"{name}未配置，请在 .env 文件中设置 {key}")

        # 检查邮箱配置
        if self.TEMP_MAIL != "null":
            if not self.check_is_valid(self.TEMP_MAIL):
                raise ValueError("临时邮箱未配置，请在 .env 文件中设置 TEMP_MAIL")
        else:
            imap_configs = {
                "IMAP_SERVER": "IMAP服务器",
                "IMAP_PORT": "IMAP端口",
                "IMAP_USER": "IMAP用户名",
                "IMAP_PASS": "IMAP密码",
            }
            for key, name in imap_configs.items():
                if not self.check_is_valid(getattr(self, key)):
                    raise ValueError(f"{name}未配置，请在 .env 文件中设置 {key}")

    def check_is_valid(self, value):
        """
        检查配置项是否有效
        
        Args:
            value: 要检查的配置值
            
        Returns:
            bool: 配置项是否有效
        """
        return isinstance(value, str) and len(str(value).strip()) > 0

    def print_config(self):
        """
        打印配置信息
        
        以易读的格式输出当前的配置信息，
        用于调试和确认配置是否正确
        """
        logger.info("=== 当前配置信息 ===")
        if self.IMAP_SERVER:
            logger.info(f"IMAP服务器: {self.IMAP_SERVER}")
            logger.info(f"IMAP端口: {self.IMAP_PORT}")
            logger.info(f"IMAP用户名: {self.IMAP_USER}")
            logger.info(f"IMAP密码: {'*' * len(self.IMAP_PASS)}")
            logger.info(f"IMAP收件箱目录: {self.IMAP_DIR}")
        else:
            logger.info(f"临时邮箱: {self.TEMP_MAIL}{self.TEMP_MAIL_EXT}")
        
        logger.info(f"浏览器类型: {self.BROWSER_TYPE}")
        logger.info(f"无头模式: {self.HEADLESS}")
        logger.info("=== 配置信息结束 ===")

if __name__ == "__main__":
    try:
        config = Config()
        logger.info("环境变量加载成功！")
        config.print_config()
    except ValueError as e:
        logger.error(f"错误: {e}") 