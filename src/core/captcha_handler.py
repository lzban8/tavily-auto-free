"""
验证码处理模块

这个模块负责处理注册过程中的验证码识别和输入，主要功能包括：
- 验证码图片获取和保存
- 验证码识别（使用 ddddocr）
- 验证码输入和提交
- 密码输入处理
- 验证结果检查

使用 ddddocr 作为 OCR 引擎，提供了稳定的验证码识别能力。
"""

import os
import base64
import logging
import time
import ddddocr
import random
import string
from io import BytesIO
from PIL import Image
from utils.logger import setup_logger
from datetime import datetime
import numpy as np
from PIL import ImageEnhance, ImageFilter
from config import Config

logger = setup_logger()

class CaptchaHandler:
    """
    验证码处理类
    
    负责处理整个验证码识别和输入流程，包括：
    - 验证码图片定位和获取
    - OCR 识别
    - 验证码输入
    - 验证结果检查
    - 密码输入处理
    """

    def __init__(self, page, config=None):
        """
        初始化验证码处理器
        
        Args:
            page: DrissionPage 页面对象
            config: 配置对象，可选
        """
        self.page = page
        self.config = config if config else Config()
        # 初始化 ddddocr，使用基本配置
        self.ocr = ddddocr.DdddOcr(show_ad=False)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # 设置截图保存目录
        self.screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.captcha_attempts = 0  # 验证码尝试计数器

    def verify_captcha(self, browser):
        """
        验证码处理主流程
        
        包括：
        1. 查找验证码图片
        2. 识别验证码
        3. 输入验证码
        4. 提交验证
        5. 检查验证结果
        
        Args:
            browser: 浏览器工具实例
            
        Returns:
            bool: 验证是否成功
        """
        try:
            while True:  # 无限循环，直到验证成功
                self.captcha_attempts += 1  # 增加计数器
                logging.info(f"开始第 {self.captcha_attempts} 轮验证码识别...")
                time.sleep(3)  # 等待验证码加载

                # 查找验证码图片
                logging.info("开始查找验证码图片...")
                captcha_img = self._get_captcha_image()
                if not captcha_img:
                    logging.error("未找到验证码图片，等待3秒后重试...")
                    time.sleep(3)
                    continue

                # 识别验证码
                captcha_text = self._recognize_captcha(captcha_img)
                if not captcha_text:
                    logging.error("验证码识别失败，等待3秒后重试...")
                    time.sleep(3)
                    continue

                # 输入验证码前等待1秒
                time.sleep(1)
                logging.info("等待1秒后开始输入验证码...")

                # 输入验证码
                if not self._input_captcha(captcha_text):
                    logging.error("验证码输入失败，等待3秒后重试...")
                    time.sleep(3)
                    continue

                # 输入后等待1秒
                time.sleep(1)
                logging.info("等待1秒后点击Continue按钮...")

                # 点击 Continue 按钮
                if not self._click_continue_button():
                    logging.error("点击Continue按钮失败，等待3秒后重试...")
                    time.sleep(3)
                    continue

                # 等待验证结果
                time.sleep(3)
                
                # 检查是否验证成功
                js_code = """
                // 检查是否存在错误提示
                const errorElement = document.querySelector('.error-message') || 
                                   document.querySelector('[role="alert"]') ||
                                   document.querySelector('.text-error');
                if (errorElement && errorElement.offsetParent !== null) {
                    return false;  // 存在错误提示，验证失败
                }
                
                // 检查是否存在密码输入框
                const passwordInput = document.querySelector('#password') ||
                                    document.querySelector('input[type="password"]') ||
                                    document.querySelector('input[name="password"]');
                                    
                // 检查密码输入框是否可见
                if (passwordInput && passwordInput.offsetParent !== null) {
                    const style = window.getComputedStyle(passwordInput);
                    return style.display !== 'none' && 
                           style.visibility !== 'hidden' && 
                           style.opacity !== '0' &&
                           passwordInput.offsetWidth > 0 &&
                           passwordInput.offsetHeight > 0;
                }
                
                return false;  // 默认返回失败
                """
                
                verification_success = self.page.run_js(js_code)
                
                if verification_success:
                    logging.info(f"第 {self.captcha_attempts} 次尝试验证码验证成功！")
                    time.sleep(2)  # 等待页面完全加载
                    return True
                    
                logging.warning(f"第 {self.captcha_attempts} 次验证码验证失败，将尝试新的验证码...")
                time.sleep(3)
                continue
                
        except Exception as e:
            logging.error(f"验证码处理过程出错: {str(e)}")
            time.sleep(3)
            return False

    def _get_captcha_image(self):
        """
        获取验证码图片元素
        
        使用多种选择器策略查找验证码图片：
        1. 通过 alt 属性
        2. 通过 src 属性
        3. 通过标签和上下文
        
        Returns:
            element: 验证码图片元素，如果未找到则返回 None
        """
        try:
            logging.info("尝试通过 JavaScript 获取验证码图片...")
            js_code = """
            return document.querySelector('img[alt="captcha"]') || 
                   document.querySelector('img[src*="image/svg+xml"]') ||
                   Array.from(document.getElementsByTagName('img')).find(img => 
                       img.src && (img.src.includes('captcha') || img.src.includes('svg'))
                   );
            """
            captcha_img = self.page.run_js(js_code)
            
            if not captcha_img:
                logging.warning("通过 JavaScript 未找到验证码图片，尝试其他选择器...")
                selectors = [
                    'img[alt="captcha"]',
                    'img[src*="svg+xml"]',
                    'form img',
                    'div img'
                ]
                for selector in selectors:
                    logging.info(f"尝试使用选择器 {selector} 查找验证码图片...")
                    elements = self.page.eles(selector)
                    for element in elements:
                        src = element.attr('src')
                        if src and ('captcha' in src.lower() or 'svg' in src.lower()):
                            logging.info(f"使用选择器 {selector} 找到验证码图片")
                            return element
            return captcha_img

        except Exception as e:
            logging.error(f"获取验证码图片失败: {str(e)}")
            return None

    def _recognize_captcha(self, captcha_img):
        """
        识别验证码
        
        流程包括：
        1. 保存验证码图片
        2. 使用 OCR 识别
        3. 过滤和验证结果
        
        Args:
            captcha_img: 验证码图片元素
            
        Returns:
            str: 识别出的验证码文本，失败返回 None
        """
        if not captcha_img:
            return None
            
        # 保存验证码图片
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        png_path = f"{self.screenshots_dir}/captcha_{timestamp}.png"
        
        try:
            # 获取验证码图片的截图
            captcha_img.get_screenshot(png_path)
            logging.info(f"验证码图片已保存: {png_path}")
            
            # 使用本地OCR识别验证码
            with open(png_path, 'rb') as f:
                image_bytes = f.read()
            
            # 识别验证码
            result = self.ocr.classification(image_bytes)
            logging.info(f"原始识别结果: {result}")
            
            # 过滤结果，只保留字母和数字
            filtered_result = ''.join(c for c in result if c.isalnum())
            logging.info(f"过滤后的识别结果: {filtered_result}")
            
            # 验证结果
            if len(filtered_result) != 6:
                logging.warning(f"验证码长度不是6位: {len(filtered_result)}")
            
            if not any(c.isupper() for c in filtered_result):
                logging.warning("验证码必须包含大小写字母")
            
            logging.info(f"验证码识别结果: {filtered_result}")
            return filtered_result
            
        except Exception as e:
            logging.error(f"识别验证码失败: {str(e)}")
            return None

    def _input_captcha(self, captcha_text):
        """
        输入验证码
        
        流程包括：
        1. 查找验证码输入框
        2. 清空输入框
        3. 输入验证码
        
        Args:
            captcha_text: 要输入的验证码文本
            
        Returns:
            bool: 是否成功输入
        """
        try:
            logging.info("查找验证码输入框...")
            captcha_input = self.page.ele('#captcha')
            
            if not captcha_input:
                logging.info("通过ID未找到输入框，尝试其他选择器...")
                js_code = """
                return document.querySelector('input[name="captcha"]') ||
                       document.querySelector('input._input-captcha') ||
                       Array.from(document.getElementsByTagName('input')).find(input => {
                           return input.className.includes('input-captcha') ||
                                  (input.type === 'text' && input.required &&
                                   input.autocapitalize === 'none' && input.spellcheck === 'false');
                       });
                """
                captcha_input = self.page.run_js(js_code)
            
            if not captcha_input:
                logging.error("未找到验证码输入框")
                return False
            
            # 清空输入框并输入验证码
            captcha_input.clear()
            captcha_input.input(captcha_text)
            logging.info("验证码输入完成")
            return True
            
        except Exception as e:
            logging.error(f"验证码输入过程出错: {str(e)}")
            return False

    def _click_continue_button(self):
        """
        点击 Continue 按钮
        
        使用多种选择器策略查找并点击按钮：
        1. 通过 type 属性
        2. 通过类名
        3. 通过文本内容
        
        Returns:
            bool: 是否成功点击
        """
        try:
            logging.info("查找 Continue 按钮...")
            js_code = """
            return document.querySelector('button[type="submit"]') || 
                   document.querySelector('button._button-login-id') ||
                   document.querySelector('button[data-action-button-primary="true"]') ||
                   document.querySelector('button.c54742484.c5494d417') ||
                   Array.from(document.getElementsByTagName('button')).find(button => 
                       button.textContent.toLowerCase().includes('continue')
                   );
            """
            continue_button = self.page.run_js(js_code)
            
            if not continue_button:
                logging.error("未找到Continue按钮")
                return False
            
            continue_button.click()
            logging.info("已点击Continue按钮")
            return True
            
        except Exception as e:
            logging.error(f"点击Continue按钮过程出错: {str(e)}")
            return False

    def handle_password_input(self, browser):
        """
        处理密码输入流程
        
        流程包括：
        1. 获取密码
        2. 查找密码输入框
        3. 输入密码
        4. 查找并点击 Continue 按钮
        
        Args:
            browser: 浏览器工具实例
            
        Returns:
            bool: 密码处理是否成功
        """
        try:
            # 从config对象中获取密码
            password = browser.config.PASSWORD  # 从browser对象的config中获取密码
            if not password:
                self.logger.error("未找到随机生成的密码")
                return False
            
            # 查找密码输入框
            self.logger.info("开始查找密码输入框...")
            
            # 主选择器 - 使用ID
            password_input = browser.page.ele('#password')
            if password_input:
                self.logger.info("使用 ID 选择器 #password 找到密码输入框")
                time.sleep(1)
                if not self._handle_input(password_input, password, "密码"):
                    return False
                    
                # 查找并点击 Continue 按钮
                self.logger.info("正在查找密码页面的 Continue 按钮...")
                time.sleep(2)  # 等待按钮加载
                
                # 使用精确的选择器组合
                js_code = """
                return document.querySelector('button._button-login-password[data-action-button-primary="true"]') ||
                       document.querySelector('button.c54742484.c5494d417') ||
                       document.querySelector('button[type="submit"][value="default"]') ||
                       Array.from(document.getElementsByTagName('button')).find(button => 
                           button.textContent === 'Continue' &&
                           button.classList.contains('_button-login-password')
                       );
                """
                continue_button = browser.page.run_js(js_code)
                
                if continue_button:
                    self.logger.info("找到密码页面的Continue按钮")
                    time.sleep(1)
                    continue_button.click()
                    self.logger.info("点击密码页面的Continue按钮")
                    time.sleep(2)
                    return True
                else:
                    self.logger.error("未找到密码页面的Continue按钮")
                    return False
            
            # 备选选择器 - 使用精确的类名和属性组合
            alternative_selectors = [
                'input.c8429dee9.c14adeb19',  # 使用完整的类名
                'input[name="password"][type="password"]',  # 使用name和type属性组合
                'input[type="password"][autocomplete="current-password"]',  # 使用type和autocomplete属性组合
                'input[type="password"][required][autofocus]'  # 使用type、required和autofocus属性组合
            ]
            
            for selector in alternative_selectors:
                self.logger.info(f"尝试使用备选选择器: {selector}")
                input_el = browser.page.ele(selector, timeout=3)
                if input_el:
                    self.logger.info(f"使用选择器 {selector} 找到密码输入框")
                    time.sleep(1)
                    if not self._handle_input(input_el, password, "密码"):
                        return False
                        
                    # 查找并点击 Continue 按钮
                    self.logger.info("正在查找密码页面的 Continue 按钮...")
                    time.sleep(2)  # 等待按钮加载
                    
                    continue_button = browser.page.run_js(js_code)
                    if continue_button:
                        self.logger.info("通过JavaScript找到密码页面的Continue按钮")
                        time.sleep(1)
                        continue_button.click()
                        self.logger.info("点击密码页面的Continue按钮")
                        time.sleep(2)
                        return True
                    else:
                        self.logger.error("未找到密码页面的Continue按钮")
                        return False
            
            # 如果还是没找到，尝试通过JavaScript查找
            self.logger.info("尝试通过JavaScript查找密码输入框...")
            js_code_input = """
            return document.querySelector('#password') || 
                   document.querySelector('input.c8429dee9.c14adeb19') ||
                   document.querySelector('input[type="password"][required][autofocus]') ||
                   Array.from(document.getElementsByTagName('input')).find(input => {
                       return input.type === 'password' &&
                              input.required &&
                              input.autocomplete === 'current-password' &&
                              input.autocapitalize === 'none';
                   });
            """
            try:
                password_input = browser.page.run_js(js_code_input)
                if password_input:
                    self.logger.info("通过JavaScript找到密码输入框")
                    time.sleep(1)
                    if not self._handle_input(password_input, password, "密码"):
                        return False
                        
                    # 查找并点击 Continue 按钮
                    self.logger.info("正在查找密码页面的 Continue 按钮...")
                    time.sleep(2)  # 等待按钮加载
                    
                    continue_button = browser.page.run_js(js_code)
                    if continue_button:
                        self.logger.info("通过JavaScript找到密码页面的Continue按钮")
                        time.sleep(1)
                        continue_button.click()
                        self.logger.info("点击密码页面的Continue按钮")
                        time.sleep(2)
                        return True
                    else:
                        self.logger.error("未找到密码页面的Continue按钮")
                        return False
            except Exception as e:
                self.logger.warning(f"JavaScript查找失败: {str(e)}")
            
            self.logger.error("未找到密码输入框")
            return False
            
        except Exception as e:
            self.logger.error(f"密码处理失败: {str(e)}")
            return False

    def _handle_input(self, input_element, text, field_name=""):
        """
        通用输入处理
        
        提供统一的输入处理逻辑：
        1. 输入前等待
        2. 执行输入
        3. 输入后等待
        4. 错误处理
        
        Args:
            input_element: 输入框元素
            text: 要输入的文本
            field_name: 字段名称（用于日志）
            
        Returns:
            bool: 是否输入成功
        """
        try:
            # 输入前等待
            time.sleep(1)
            # 输入文本
            input_element.input(text)
            self.logger.info(f"已输入{field_name}: {text}")
            # 输入后等待
            time.sleep(1)
            return True
        except Exception as e:
            self.logger.error(f"{field_name}输入失败: {str(e)}")
            return False 