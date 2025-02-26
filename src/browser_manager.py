from DrissionPage import ChromiumOptions, ChromiumPage
import sys
import os
import logging
from typing import Dict, Any, Optional

class BrowserManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.page = None
        self.logger = logging.getLogger(__name__)
        self._setup_browser()

    def _setup_browser(self):
        """设置浏览器配置"""
        try:
            # 创建浏览器选项
            co = ChromiumOptions()
            
            # 设置用户代理
            if 'user_agent' in self.config:
                co.set_argument(f'--user-agent={self.config["user_agent"]}')
            
            # 设置代理
            if 'proxy' in self.config and self.config['proxy']:
                co.set_argument(f'--proxy-server={self.config["proxy"]}')
            
            # 设置无头模式
            if 'headless' in self.config and self.config['headless']:
                co.set_argument('--headless')
            
            # 禁用保存密码提示
            co.set_pref("credentials_enable_service", False)
            
            # 隐藏崩溃恢复气泡
            co.set_argument("--hide-crash-restore-bubble")
            
            # Mac系统特殊处理
            if sys.platform == "darwin":
                co.set_argument("--no-sandbox")
                co.set_argument("--disable-gpu")
            
            # 创建页面对象
            self.page = ChromiumPage(co)
            self.logger.info("浏览器初始化成功")
            
        except Exception as e:
            self.logger.error(f"浏览器初始化失败: {str(e)}")
            raise

    def navigate_to(self, url: str) -> bool:
        """导航到指定URL"""
        try:
            self.page.get(url)
            return True
        except Exception as e:
            self.logger.error(f"导航到 {url} 失败: {str(e)}")
            return False

    def find_element(self, by: str, value: str, timeout: float = 10) -> Optional[object]:
        """查找元素"""
        try:
            # 使用DrissionPage的选择器语法
            selector = value
            if by == 'name':
                selector = f'@name={value}'
            elif by == 'id':
                selector = f'@id={value}'
            elif by == 'class':
                selector = f'.{value}'
            
            ele = self.page.ele(selector, timeout=timeout)
            return ele if ele.exists else None
            
        except Exception as e:
            self.logger.warning(f"未找到元素 {value}")
            return None

    def input_text(self, element: object, text: str) -> bool:
        """输入文本"""
        try:
            # 使用DrissionPage的actions接口
            element.click()
            element.input(text)
            return True
        except Exception as e:
            self.logger.error(f"输入文本失败: {str(e)}")
            return False

    def click_element(self, element: object) -> bool:
        """点击元素"""
        try:
            element.click()
            return True
        except Exception as e:
            self.logger.error(f"点击元素失败: {str(e)}")
            return False

    def get_element_text(self, element: object) -> Optional[str]:
        """获取元素文本"""
        try:
            return element.text
        except Exception as e:
            self.logger.error(f"获取元素文本失败: {str(e)}")
            return None

    def save_screenshot(self, filename: str) -> bool:
        """保存页面截图"""
        try:
            self.page.get_screenshot(filename)
            self.logger.info(f"截图已保存: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"保存截图失败: {str(e)}")
            return False

    def get_cookies(self) -> Dict:
        """获取所有cookie"""
        try:
            return self.page.cookies
        except Exception as e:
            self.logger.error(f"获取cookies失败: {str(e)}")
            return {}

    def close(self):
        """关闭浏览器"""
        try:
            if self.page:
                self.page.quit()
                self.logger.info("浏览器已关闭")
        except Exception as e:
            self.logger.error(f"关闭浏览器失败: {str(e)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 