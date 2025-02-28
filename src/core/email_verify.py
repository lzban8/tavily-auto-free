"""
邮箱验证模块

这个模块负责处理邮箱验证相关的功能，主要包括：
- 临时邮箱的管理
- 验证码邮件的获取
- 验证码的提取
- 邮件的清理

使用临时邮箱 API 实现邮箱验证功能，支持自动重试和错误处理。
"""

import os
import re
import time
import json
import logging
import requests
from datetime import datetime
from config import Config

from utils.logger import setup_logger

class EmailVerificationHandler:
    """
    邮箱验证处理类
    
    负责处理整个邮箱验证流程，包括：
    - 获取验证码邮件
    - 提取验证码
    - 清理已处理的邮件
    - 错误处理和重试
    """

    def __init__(self):
        """
        初始化邮箱验证处理器
        
        从配置中获取：
        - 临时邮箱 API 地址
        - 邮箱域名
        """
        self.config = Config()
        self.base_url = self.config.TEMP_MAIL_API_URL
        self.domain = self.config.DOMAIN

    def get_verification_code(self, max_retries=5, retry_interval=10):
        """
        获取验证码
        
        通过多次尝试从邮件中获取验证码，支持重试机制
        
        Args:
            max_retries (int): 最大重试次数
            retry_interval (int): 重试间隔（秒）
            
        Returns:
            str: 验证码，如果获取失败则返回 None
        """
        try:
            for attempt in range(max_retries):
                logging.info(f"尝试获取验证码 (第 {attempt + 1} 次)")
                code = self._get_latest_mail_code()
                
                if code:
                    return code
                
                if attempt < max_retries - 1:
                    logging.info(f"等待 {retry_interval} 秒后重试...")
                    time.sleep(retry_interval)
            
            logging.error(f"在 {max_retries} 次尝试后未能获取验证码")
            return None

        except Exception as e:
            logging.error(f"获取验证码时出错: {str(e)}")
            return None

    def _get_latest_mail_code(self):
        """
        获取最新邮件中的验证码
        
        流程包括：
        1. 获取邮件列表
        2. 获取最新邮件内容
        3. 提取验证码
        4. 清理已处理的邮件
        
        Returns:
            str: 验证码，如果获取失败则返回 None
        """
        try:
            # 构建 API URL
            api_url = f"{self.base_url}/mail/id"
            
            # 发送请求获取邮件列表
            response = requests.get(api_url)
            if response.status_code != 200:
                logging.error(f"获取邮件列表失败: {response.status_code}")
                return None
            
            mail_list = response.json()
            if not mail_list:
                logging.info("邮箱为空")
                return None

            # 获取最新邮件的内容
            latest_mail_id = mail_list[0]
            mail_content_url = f"{self.base_url}/mail/{latest_mail_id}/content"
            
            response = requests.get(mail_content_url)
            if response.status_code != 200:
                logging.error(f"获取邮件内容失败: {response.status_code}")
                return None

            mail_content = response.json()
            if not mail_content:
                logging.error("邮件内容为空")
                return None

            # 使用正则表达式提取验证码
            mail_text = mail_content.get('text', '')
            code_match = re.search(r"(?<![a-zA-Z@.])\b\d{6}\b", mail_text)
            
            if code_match:
                code = code_match.group()
                logging.info(f"成功提取验证码: {code}")
                self._cleanup_mail(latest_mail_id)
                return code
            else:
                logging.info("未找到验证码")
                return None

        except Exception as e:
            logging.error(f"获取最新邮件验证码时出错: {str(e)}")
            return None

    def _cleanup_mail(self, mail_id, max_retries=3):
        """
        清理已处理的邮件
        
        支持多次重试的邮件删除操作
        
        Args:
            mail_id (str): 要删除的邮件ID
            max_retries (int): 最大重试次数
            
        Returns:
            bool: 是否成功删除
        """
        for attempt in range(max_retries):
            try:
                delete_url = f"{self.base_url}/mail/{mail_id}"
                response = requests.delete(delete_url)
                
                if response.status_code == 200:
                    logging.info(f"成功删除邮件 {mail_id}")
                    return True
                    
                logging.warning(f"删除邮件失败 (尝试 {attempt + 1}/{max_retries})")
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"删除邮件时出错: {str(e)}")
                
        return False

if __name__ == "__main__":
    # 测试代码
    handler = EmailVerificationHandler()
    try:
        code = handler.get_verification_code()
        print(f"获取到的验证码: {code}")
    except Exception as e:
        print(f"错误: {str(e)}") 