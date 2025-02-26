import imaplib
import email
import re
import time
import logging
from typing import Dict, Any, Optional
from email.header import decode_header

class EmailHandler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.mail = None

    def connect(self) -> bool:
        """连接到邮件服务器"""
        try:
            self.mail = imaplib.IMAP4_SSL(
                self.config['imap_server'],
                self.config['imap_port']
            )
            self.mail.login(
                self.config['imap_user'],
                self.config['imap_pass']
            )
            self.logger.info("邮箱连接成功")
            return True
        except Exception as e:
            self.logger.error(f"邮箱连接失败: {str(e)}")
            return False

    def get_verification_code(self, sender: str = "tavily.com", max_retries: int = 5, retry_interval: int = 10) -> Optional[str]:
        """获取验证码"""
        if not self.mail:
            if not self.connect():
                return None

        for attempt in range(max_retries):
            try:
                self.mail.select(self.config['imap_dir'])
                
                # 搜索来自特定发件人的邮件
                _, messages = self.mail.search(None, f'(FROM "{sender}")')
                
                if not messages[0]:
                    if attempt < max_retries - 1:
                        self.logger.info(f"未找到验证码邮件，{retry_interval}秒后重试...")
                        time.sleep(retry_interval)
                        continue
                    else:
                        self.logger.warning("达到最大重试次数，仍未找到验证码邮件")
                        return None

                # 获取最新邮件
                latest_email_id = messages[0].split()[-1]
                _, msg_data = self.mail.fetch(latest_email_id, '(RFC822)')
                email_body = msg_data[0][1]
                
                # 解析邮件
                email_message = email.message_from_bytes(email_body)
                
                # 获取邮件内容
                body = self._get_email_body(email_message)
                if body:
                    # 查找验证码（假设是6位数字）
                    code_match = re.search(r'\b\d{6}\b', body)
                    if code_match:
                        code = code_match.group()
                        self.logger.info(f"成功获取验证码: {code}")
                        return code

                if attempt < max_retries - 1:
                    self.logger.info(f"未在邮件中找到验证码，{retry_interval}秒后重试...")
                    time.sleep(retry_interval)
                    
            except Exception as e:
                self.logger.error(f"获取验证码时发生错误: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
                else:
                    return None

        return None

    def _get_email_body(self, email_message) -> Optional[str]:
        """获取邮件内容"""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        return part.get_payload(decode=True).decode()
            else:
                return email_message.get_payload(decode=True).decode()
        except Exception as e:
            self.logger.error(f"解析邮件内容失败: {str(e)}")
            return None

    def close(self):
        """关闭邮箱连接"""
        try:
            if self.mail:
                self.mail.close()
                self.mail.logout()
                self.logger.info("邮箱连接已关闭")
        except Exception as e:
            self.logger.error(f"关闭邮箱连接失败: {str(e)}")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 