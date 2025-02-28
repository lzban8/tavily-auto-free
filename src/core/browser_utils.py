"""
浏览器工具模块

这个模块提供了浏览器自动化的核心功能，包括：
- 浏览器的启动和配置
- 页面导航和等待
- 元素查找和交互
- 存储清理
- 截图功能

使用 DrissionPage 作为底层实现，提供了更稳定和高效的浏览器自动化能力。
"""

import os
import time
import logging
from DrissionPage import ChromiumPage, ChromiumOptions
from utils.logger import setup_logger

logger = setup_logger()

class BrowserUtils:
    """
    浏览器工具类
    
    封装了浏览器的常用操作，包括：
    - 启动和关闭浏览器
    - 页面导航
    - 元素查找和操作
    - 存储清理
    """

    def __init__(self, config=None, headless=True):
        """
        初始化浏览器工具类
        
        Args:
            config (Config): 配置对象，包含浏览器相关配置
            headless (bool): 是否使用无头模式运行浏览器
        """
        self.config = config
        self.headless = headless
        self.page = None

    def start(self):
        """
        启动浏览器
        
        配置并启动 Chrome 浏览器，包括：
        - 设置无头模式
        - 配置浏览器参数
        - 清理浏览器数据
        - 设置窗口大小
        
        Returns:
            bool: 浏览器是否成功启动
        """
        try:
            from DrissionPage import ChromiumOptions
            
            # 创建浏览器选项
            co = ChromiumOptions()
            
            # 添加清理浏览器数据的参数
            co.set_argument('--incognito')  # 使用隐私模式
            co.set_argument('--disable-site-isolation-trials')
            co.set_argument('--disable-extensions')
            co.set_argument('--disable-sync')
            co.set_argument('--no-default-browser-check')
            co.set_argument('--no-first-run')
            co.set_argument('--no-sandbox')
            co.set_argument('--start-maximized')
            
            # 设置用户数据目录为临时目录
            temp_dir = os.path.join(os.getcwd(), "temp_browser_data")
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            co.set_argument(f'--user-data-dir={temp_dir}')
            
            if self.headless:
                co.set_argument('--headless')
            
            if self.config and hasattr(self.config, 'BROWSER_USER_AGENT'):
                co.set_argument(f'--user-agent={self.config.BROWSER_USER_AGENT}')
            
            # 设置窗口大小
            width = self.config.BROWSER_WIDTH if self.config and hasattr(self.config, 'BROWSER_WIDTH') else 1920
            height = self.config.BROWSER_HEIGHT if self.config and hasattr(self.config, 'BROWSER_HEIGHT') else 1080
            co.set_argument(f'--window-size={width},{height}')
            
            # 创建浏览器实例
            self.page = ChromiumPage(co)
            
            logging.info("浏览器启动成功")
            return True
            
        except Exception as e:
            logging.error(f"浏览器启动失败: {str(e)}")
            return False

    def _clear_storage(self):
        """
        清除浏览器存储
        
        清除以下类型的存储：
        - localStorage
        - sessionStorage
        - cookies
        """
        try:
            # 清理 cookies
            self.page.run_js("""
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i];
                    const eqPos = cookie.indexOf('=');
                    const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
                    document.cookie = name + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';
                }
            """)
            # 清理 localStorage
            self.page.run_js("localStorage.clear();")
            # 清理 sessionStorage
            self.page.run_js("sessionStorage.clear();")
            logging.info("浏览器存储清理完成")
        except Exception as e:
            logging.error(f"清理存储失败: {str(e)}")

    def close(self):
        """
        关闭浏览器并清理临时文件
        """
        try:
            if self.page:
                self.page.quit()
                
            # 清理临时目录
            temp_dir = os.path.join(os.getcwd(), "temp_browser_data")
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
                
            logging.info("浏览器已关闭")
        except Exception as e:
            logging.error(f"关闭浏览器时出错: {str(e)}")

    def navigate_to(self, url, max_retries=3, wait_time=5):
        """
        导航到指定URL
        
        Args:
            url: 目标URL
            max_retries: 最大重试次数
            wait_time: 每次等待时间（秒）
            
        Returns:
            bool: 是否成功导航
        """
        logging.info(f"正在导航到 {url}")
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logging.info(f"第 {attempt + 1} 次尝试导航...")
                
                # 导航到页面
                self.page.get(url)
                
                # 等待页面加载
                time.sleep(wait_time)
                
                # 检查页面是否完全加载
                is_loaded = self.page.run_js("""
                    return document.readyState === 'complete' && 
                           !document.querySelector('.loading-indicator');
                """)
                
                if is_loaded:
                    # 额外等待以确保页面稳定
                    time.sleep(2)
                    return True
                    
            except Exception as e:
                logging.warning(f"导航失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                
            time.sleep(wait_time)
            
        logging.error(f"多次尝试后仍无法导航到 {url}")
        return False

    def wait_and_click(self, selector, timeout=10, check_interval=0.5):
        """
        等待元素出现并点击
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            bool: 是否成功点击
        """
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                element = self.page.ele(selector, timeout=1)
                if element:
                    time.sleep(1)  # 等待元素稳定
                    element.click()
                    time.sleep(1)  # 等待点击后的响应
                    return True
                time.sleep(check_interval)
                
            logging.error(f"等待元素超时: {selector}")
            return False
            
        except Exception as e:
            logging.error(f"点击元素失败: {str(e)}")
            return False

    def wait_and_type(self, selector, text, timeout=10, check_interval=0.5):
        """
        等待元素出现并输入文本
        
        Args:
            selector: 元素选择器
            text: 要输入的文本
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            bool: 是否成功输入
        """
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                element = self.page.ele(selector, timeout=1)
                if element:
                    time.sleep(1)  # 等待元素稳定
                    element.clear()  # 清空现有内容
                    time.sleep(0.5)
                    element.input(text)
                    time.sleep(1)  # 等待输入完成
                    return True
                time.sleep(check_interval)
                
            logging.error(f"等待元素超时: {selector}")
            return False
            
        except Exception as e:
            logging.error(f"输入文本失败: {str(e)}")
            return False

    def wait_for_navigation(self, timeout=30, check_interval=0.5):
        """
        等待页面导航完成
        
        Args:
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            bool: 是否成功等待
        """
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                is_loaded = self.page.run_js("""
                    return document.readyState === 'complete' && 
                           !document.querySelector('.loading-indicator');
                """)
                
                if is_loaded:
                    time.sleep(2)  # 额外等待以确保页面稳定
                    return True
                    
                time.sleep(check_interval)
                
            logging.error("等待页面导航超时")
            return False
            
        except Exception as e:
            logging.error(f"等待页面导航失败: {str(e)}")
            return False

    def get_cookies(self):
        """
        获取所有cookies
        
        Returns:
            list: cookies list
        """
        try:
            return self.page.get_cookies()
        except Exception as e:
            logging.error(f"获取cookies失败: {str(e)}")
            return None

    def save_screenshot(self, path):
        """
        保存页面截图
        
        Args:
            path: 截图保存路径
            
        Returns:
            bool: 是否成功保存
        """
        try:
            self.page.get_screenshot(path)
            logging.info(f"截图已保存到 {path}")
            return True
        except Exception as e:
            logging.error(f"保存截图失败: {str(e)}")
            return False 