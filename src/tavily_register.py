from selenium.webdriver.common.by import By
import logging
import time
from typing import Optional, Tuple

from config.config import Config
from .browser_manager import BrowserManager
from .email_handler import EmailHandler
from .logger import Logger

class TavilyRegister:
    def __init__(self):
        # 初始化配置
        self.config = Config()
        
        # 初始化日志
        self.logger = Logger(self.config.get_log_config()).get_logger()
        
        # 初始化浏览器管理器
        self.browser = None
        
        # 初始化邮件处理器
        self.email_handler = None

    def setup(self):
        """初始化必要的组件"""
        try:
            self.browser = BrowserManager(self.config.get_browser_config())
            self.email_handler = EmailHandler(self.config.get_email_config())
            return True
        except Exception as e:
            self.logger.error(f"初始化组件失败: {str(e)}")
            return False

    def register_account(self, email: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        注册Tavily账户
        
        Args:
            email: 注册邮箱
            password: 注册密码
            
        Returns:
            (bool, str): (是否成功, API密钥)
        """
        try:
            if not self.setup():
                return False, None

            # 1. 访问注册页面
            if not self.browser.navigate_to(self.config.TAVILY_SIGNUP_URL):
                return False, None

            # 2. 填写注册表单
            email_input = self.browser.find_element(By.NAME, "email")
            password_input = self.browser.find_element(By.NAME, "password")
            
            if not all([email_input, password_input]):
                self.logger.error("未找到注册表单元素")
                return False, None

            if not all([
                self.browser.input_text(email_input, email),
                self.browser.input_text(password_input, password)
            ]):
                return False, None

            # 3. 提交注册表单
            submit_button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
            if not submit_button or not self.browser.click_element(submit_button):
                self.logger.error("提交注册表单失败")
                return False, None

            # 4. 等待并处理验证码
            time.sleep(5)  # 等待验证码邮件发送
            verification_code = self.email_handler.get_verification_code()
            
            if not verification_code:
                self.logger.error("获取验证码失败")
                return False, None

            # 5. 输入验证码
            code_input = self.browser.find_element(By.NAME, "code")
            if not code_input or not self.browser.input_text(code_input, verification_code):
                self.logger.error("输入验证码失败")
                return False, None

            # 6. 提交验证码
            verify_button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
            if not verify_button or not self.browser.click_element(verify_button):
                self.logger.error("提交验证码失败")
                return False, None

            # 7. 等待跳转到仪表板页面
            time.sleep(5)

            # 8. 获取API密钥
            api_key = self._get_api_key()
            if not api_key:
                self.logger.error("获取API密钥失败")
                return False, None

            self.logger.info("注册成功并获取到API密钥")
            return True, api_key

        except Exception as e:
            self.logger.error(f"注册过程发生错误: {str(e)}")
            return False, None
        
        finally:
            self.cleanup()

    def _get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        try:
            # 导航到API页面
            if not self.browser.navigate_to(self.config.TAVILY_API_URL):
                return None

            # 等待API密钥元素出现
            api_key_element = self.browser.find_element(
                By.XPATH,
                "//div[contains(text(), 'tvly-')]"
            )
            
            if not api_key_element:
                return None

            return self.browser.get_element_text(api_key_element)

        except Exception as e:
            self.logger.error(f"获取API密钥时发生错误: {str(e)}")
            return None

    def cleanup(self):
        """清理资源"""
        try:
            if self.browser:
                self.browser.close()
            if self.email_handler:
                self.email_handler.close()
        except Exception as e:
            self.logger.error(f"清理资源时发生错误: {str(e)}")

def main():
    # 使用示例
    register = TavilyRegister()
    success, api_key = register.register_account(
        email="your_email@example.com",
        password="your_password"
    )
    
    if success:
        print(f"注册成功！API密钥: {api_key}")
    else:
        print("注册失败")

if __name__ == "__main__":
    main() 