import os
from typing import Dict, Any

class Config:
    def __init__(self):
        # Tavily相关配置
        self.TAVILY_BASE_URL = "https://tavily.com"
        self.TAVILY_SIGNUP_URL = f"{self.TAVILY_BASE_URL}/auth/signup"
        self.TAVILY_API_URL = f"{self.TAVILY_BASE_URL}/dashboard"
        
        # 邮箱配置
        self.EMAIL_CONFIG = {
            'imap_server': os.getenv('IMAP_SERVER', ''),
            'imap_port': int(os.getenv('IMAP_PORT', '993')),
            'imap_user': os.getenv('IMAP_USER', ''),
            'imap_pass': os.getenv('IMAP_PASS', ''),
            'imap_dir': 'INBOX'
        }
        
        # 浏览器配置
        self.BROWSER_CONFIG = {
            'headless': False,  # 是否使用无头模式
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'window_size': (1920, 1080)
        }
        
        # 日志配置
        self.LOG_CONFIG = {
            'log_level': 'INFO',
            'log_file': 'logs/tavily_auto.log',
            'max_bytes': 10 * 1024 * 1024,  # 10MB
            'backup_count': 5
        }
        
        # 重试配置
        self.RETRY_CONFIG = {
            'max_retries': 3,
            'retry_interval': 5,
            'timeout': 10
        }
    
    def get_email_config(self) -> Dict[str, Any]:
        """获取邮箱配置"""
        return self.EMAIL_CONFIG
    
    def get_browser_config(self) -> Dict[str, Any]:
        """获取浏览器配置"""
        return self.BROWSER_CONFIG
    
    def get_log_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.LOG_CONFIG
    
    def get_retry_config(self) -> Dict[str, Any]:
        """获取重试配置"""
        return self.RETRY_CONFIG 