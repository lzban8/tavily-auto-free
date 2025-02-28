"""
Tavily API Key 自动注册工具

这个模块是整个自动化注册流程的主入口，负责协调各个组件完成注册流程。
主要功能包括：
1. 启动浏览器并进行配置
2. 生成随机邮箱和密码
3. 自动填写注册表单
4. 处理验证码
5. 获取 API Key
6. 保存账号信息

"""

import os
import sys
import time
import random
import string
import logging
from datetime import datetime
from config import Config
from core.browser_utils import BrowserUtils
from core.email_verify import EmailVerificationHandler
from core.captcha_handler import CaptchaHandler
from utils.logger import setup_logger
from utils.utils import generate_random_string, generate_email, generate_password
import csv
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化日志
logger = setup_logger()

class TavilyAutoRegister:
    """
    Tavily 自动注册类
    
    负责整个注册流程的自动化操作，包括：
    - 浏览器控制
    - 表单填写
    - 验证码处理
    - API Key 获取
    - 账号信息保存
    """

    def __init__(self):
        """初始化自动注册类的各个组件"""
        self.config = Config()  # 加载配置
        # 从.env文件读取无头模式配置
        headless = os.getenv('HEADLESS', 'true').lower() == 'true'
        self.browser = BrowserUtils(config=self.config, headless=headless)  # 初始化浏览器工具
        self.email_handler = EmailVerificationHandler()  # 初始化邮箱处理器
        self.captcha_handler = None  # 验证码处理器（延迟初始化）
        
        # 设置URL
        self.base_url = "https://app.tavily.com"
        self.signup_url = f"{self.base_url}/sign-up"
        self.dashboard_url = f"{self.base_url}/home"

    def start(self):
        """
        启动自动注册流程
        
        流程包括：
        1. 启动浏览器
        2. 生成随机账号信息
        3. 导航到注册页面
        4. 填写注册表单
        5. 获取 API Key
        6. 保存账号信息
        
        Returns:
            bool: 注册是否成功
        """
        try:
            # 启动浏览器
            if not self.browser.start():
                return False

            # 初始化验证码处理器
            self.captcha_handler = CaptchaHandler(self.browser.page)

            # 生成随机邮箱和密码
            logging.info("正在生成随机邮箱和密码...")
            email = generate_email()
            password = generate_password()
            logging.info(f"使用邮箱: {email}")
            logging.info(f"使用密码: {password}")
            
            # 保存密码到配置中
            self.config.PASSWORD = password

            # 导航到主页并处理注册流程
            if not self._handle_navigation():
                return False

            # 填写注册表单
            if not self._fill_registration_form(email, password):
                return False

            # 获取 API Key
            api_key = self._get_api_key()
            if not api_key:
                return False

            # 保存账号信息
            self._save_account_info(email, password, api_key)
            return True

        except Exception as e:
            logging.error(f"注册过程出错: {str(e)}")
            return False
        finally:
            self.browser.close()

    def _handle_navigation(self):
        """
        处理页面导航逻辑
        
        流程：
        1. 导航到首页
        2. 等待页面加载
        3. 查找并点击注册链接
        4. 等待注册页面加载
        
        Returns:
            bool: 导航是否成功
        """
        try:
            # 导航到首页
            logging.info("正在导航到首页...")
            self.browser.page.get("https://app.tavily.com")
            
            # 等待页面加载
            logging.info("等待页面加载...")
            time.sleep(10)  # 增加等待时间
            
            # 检查页面是否完全加载
            js_code = """
            return new Promise((resolve) => {
                // 检查页面加载状态
                if (document.readyState === 'complete') {
                    // 等待可能的动态内容加载
                    setTimeout(() => {
                        resolve(true);
                    }, 2000);
                } else {
                    // 如果页面还没加载完，等待 load 事件
                    window.addEventListener('load', () => {
                        setTimeout(() => {
                            resolve(true);
                        }, 2000);
                    });
                }
            });
            """
            self.browser.page.run_js(js_code)
            
            # 查找注册链接
            logging.info("正在查找注册链接...")
            js_code = """
            function findSignUpLink() {
                // 查找所有链接
                const links = Array.from(document.getElementsByTagName('a'));
                
                // 遍历所有链接
                for (const link of links) {
                    const href = link.getAttribute('href') || '';
                    const text = link.textContent.trim().toLowerCase();
                    
                    // 通过 href 或文本内容匹配
                    if (href.includes('sign-up') || 
                        href.includes('signup') || 
                        text === 'sign up' || 
                        text === 'signup' || 
                        text.includes('sign up') || 
                        text.includes('signup')) {
                        
                        console.log('找到注册链接:', {
                            href: href,
                            text: text
                        });
                        return link;
                    }
                }
                return null;
            }
            return findSignUpLink();
            """
            
            # 尝试查找注册链接
            signup_link = self.browser.page.run_js(js_code)
            
            if signup_link:
                logging.info("找到注册链接，正在点击...")
                signup_link.click()
                
                # 等待页面跳转和加载
                time.sleep(5)  # 增加等待时间
                
                # 验证是否成功跳转到注册页面
                current_url = self.browser.page.url
                if "sign-up" in current_url.lower() or "signup" in current_url.lower():
                    logging.info("成功跳转到注册页面")
                    time.sleep(3)  # 额外等待确保页面完全加载
                    return True
                else:
                    logging.error("跳转后的页面不是注册页面")
                    return False
            else:
                logging.error("未找到注册链接")
                return False
                
        except Exception as e:
            logging.error(f"导航过程出错: {str(e)}")
            return False

    def _fill_registration_form(self, email, password):
        """
        填写注册表单
        
        Args:
            email (str): 要使用的邮箱地址
            password (str): 要使用的密码
            
        Returns:
            bool: 表单填写是否成功
        """
        try:
            # 查找并填写邮箱输入框
            if not self._handle_email_input(email):
                return False

            # 处理验证码
            if not self.captcha_handler.verify_captcha(self.browser):
                logging.error("验证码处理失败")
                return False
            
            logging.info("验证码处理完成")
            time.sleep(2)
            
            # 处理密码输入
            if not self.captcha_handler.handle_password_input(self.browser):
                logging.error("密码输入处理失败")
                return False
            
            logging.info("密码输入处理完成")
            return True
            
        except Exception as e:
            logging.error(f"填写注册表单失败: {str(e)}")
            return False

    def _handle_email_input(self, email):
        """
        处理邮箱输入
        
        Args:
            email (str): 要输入的邮箱地址
            
        Returns:
            bool: 邮箱输入是否成功
        """
        logging.info("正在查找邮箱输入框...")
        js_code = """
        return document.querySelector('#email') ||
               document.querySelector('input.c8429dee9.c2ca7b14a') ||
               document.querySelector('input[inputmode="email"][autocomplete="email"]') ||
               document.querySelector('input[type="text"][name="email"][required]');
        """
        email_input = self.browser.page.run_js(js_code)
        
        if email_input:
            logging.info("找到邮箱输入框")
            time.sleep(1)
            
            email_input.clear()
            time.sleep(0.5)
            
            email_input.input(email)
            logging.info("邮箱输入完成")
            return True
        
        logging.error("未找到邮箱输入框")
        return False

    def _get_api_key(self):
        """
        获取 API Key
        
        通过网络请求获取 API Key，支持重试机制
        
        Returns:
            str: API Key 或 None（如果获取失败）
        """
        logging.info("等待仪表盘界面加载...")
        time.sleep(5)
        
        logging.info("开始尝试获取API Key...")
        api_key = self.browser.page.run_js("""
            async function getApiKey() {
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                try {
                    console.log('尝试从网络请求中获取API Key...');
                    const response = await fetch('/api/keys');
                    const data = await response.json();
                    if (data && data.length > 0 && data[0].key && data[0].key.startsWith('tvly-')) {
                        console.log('成功从网络请求获取API Key');
                        return data[0].key;
                    }
                } catch (e) {
                    console.error('从网络请求获取API Key失败:', e);
                }
                
                console.log('无法获取API Key');
                return null;
            }
            return getApiKey();
        """)
        
        if not api_key:
            logging.error("未找到API Key")
            raise Exception("未找到API Key")
        
        logging.info(f"成功获取API Key: {api_key}")
        return api_key

    def _save_account_info(self, email, password, api_key):
        """
        保存账号信息到CSV文件
        
        Args:
            email (str): 邮箱地址
            password (str): 密码
            api_key (str): API Key
        """
        try:
            filename = "accounts.csv"
            headers = ["邮箱", "密码", "API密钥", "创建时间"]
            data = [email, password, api_key, time.strftime("%Y-%m-%d %H:%M:%S")]
            
            # 检查文件是否存在
            file_exists = os.path.exists(filename)
            
            # 以追加模式打开文件，添加 BOM 头
            mode = 'a' if file_exists else 'w'
            with open(filename, mode, newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 如果文件不存在，写入表头
                if not file_exists:
                    writer.writerow(headers)
                
                # 写入数据
                writer.writerow(data)
            
            logging.info(f"账号信息已保存到 {filename}")

        except Exception as e:
            logging.error(f"保存账号信息失败: {str(e)}")

    def verify_email(self):
        """验证邮箱"""
        try:
            logging.info("等待验证邮件...")
            verification_code = self.email_handler.get_verification_code()
            if not verification_code:
                return False

            logging.info(f"获取到验证码: {verification_code}")

            # 输入验证码
            if not self.browser.wait_and_type('input[name="code"]', verification_code):
                return False

            # 点击验证按钮
            if not self.browser.wait_and_click('button[type="submit"]'):
                return False

            # 等待跳转到仪表板
            time.sleep(3)
            if "dashboard" in self.browser.page.url:
                logging.info("邮箱验证成功")
                return True
            else:
                logging.error("邮箱验证失败")
                return False

        except Exception as e:
            logging.error(f"邮箱验证过程出错: {str(e)}")
            return False

    def test_email_input(self):
        """测试邮箱输入功能"""
        try:
            if not self.browser.start():
                logging.error("浏览器启动失败")
                return False

            # 生成测试邮箱
            test_email = generate_email()
            logging.info(f"测试邮箱: {test_email}")

            # 导航到注册页面
            if not self.browser.navigate_to(self.signup_url):
                logging.error("导航到注册页面失败")
                return False

            # 等待页面加载
            time.sleep(2)
            
            # 查找邮箱输入框
            logging.info("正在查找邮箱输入框...")
            js_code = """
            return document.querySelector('#email') ||
                   document.querySelector('input.c8429dee9.c2ca7b14a') ||
                   document.querySelector('input[inputmode="email"][autocomplete="email"]') ||
                   document.querySelector('input[type="text"][name="email"][required]');
            """
            email_input = self.browser.page.run_js(js_code)
            
            if email_input:
                logging.info("找到邮箱输入框")
                time.sleep(1)
                
                # 清空输入框
                email_input.clear()
                time.sleep(0.5)
                
                # 输入邮箱
                email_input.input(test_email)
                logging.info("邮箱输入完成")
                time.sleep(1)

                # 处理验证码
                if not self.captcha_handler.verify_captcha(self.browser):
                    logging.error("验证码处理失败")
                    return False
                
                logging.info("验证码处理完成")
                time.sleep(1)

                return True
            
            logging.error("未找到邮箱输入框")
            return False

        except Exception as e:
            logging.error(f"测试过程出错: {str(e)}")
            return False
        finally:
            time.sleep(3)  # 等待一会儿以便查看结果
            self.browser.close()

    def test_password_input(self):
        """测试密码输入功能"""
        try:
            if not self.browser.start():
                logging.error("浏览器启动失败")
                return False

            # 生成测试密码
            test_password = generate_password()
            logging.info(f"测试密码: {test_password}")

            # 导航到注册页面
            if not self.browser.navigate_to(self.signup_url):
                logging.error("导航到注册页面失败")
                return False

            # 等待页面加载
            time.sleep(2)
            
            # 查找密码输入框
            logging.info("正在查找密码输入框...")
            password_input = self.browser.page.ele('#password')
            
            if password_input:
                logging.info("使用 ID 选择器 #password 找到密码输入框")
            else:
                logging.warning("ID 选择器失败，尝试其他选择器...")
                alternative_selectors = [
                    'input[name="password"]',
                    'input[type="password"]'
                ]
                
                for selector in alternative_selectors:
                    logging.info(f"尝试选择器: {selector}")
                    password_input = self.browser.page.ele(selector)
                    if password_input:
                        logging.info(f"成功使用选择器: {selector}")
                        break
            
            if not password_input:
                logging.error("所有选择器都无法找到密码输入框")
                return False

            # 输入密码
            try:
                # 清空输入框
                password_input.clear()
                time.sleep(0.5)
                
                # 输入密码
                password_input.input(test_password)
                logging.info("密码输入完成")
                time.sleep(2)  # 等待一会儿以便观察结果
                return True
                    
            except Exception as e:
                logging.error(f"输入过程出错: {str(e)}")
                return False

        except Exception as e:
            logging.error(f"测试过程出错: {str(e)}")
            return False
        finally:
            time.sleep(3)  # 等待一会儿以便查看结果
            self.browser.close()

    def test_email_and_code(self):
        """测试邮箱和验证码输入功能"""
        try:
            if not self.browser.start():
                logging.error("浏览器启动失败")
                return False

            # 生成测试邮箱和密码
            logging.info("正在生成随机邮箱和密码...")
            test_email = generate_email()
            test_password = generate_password()
            logging.info(f"生成邮箱: {test_email}")
            logging.info(f"生成密码: {test_password}")
            
            # 设置密码到config对象中
            self.config.PASSWORD = test_password

            # 初始化 CaptchaHandler，传入config对象
            self.captcha_handler = CaptchaHandler(self.browser.page, self.config)

            # 先导航到主页
            if not self.browser.navigate_to(self.dashboard_url):
                logging.error("导航到主页失败")
                return False

            # 等待页面加载
            logging.info("等待页面加载完成...")
            time.sleep(5)  # 增加等待时间

            # 查找并点击 Sign up 链接
            logging.info("正在查找 Sign up 链接...")
            js_code = """
            return document.querySelector('a[href*="/sign-up"]') ||
                   document.querySelector('a[href*="/signup"]') ||
                   Array.from(document.getElementsByTagName('a')).find(a => 
                       a.textContent.trim() === 'Sign up'
                   );
            """
            signup_link = self.browser.page.run_js(js_code)
            
            if signup_link:
                logging.info("找到 Sign up 链接，正在点击...")
                signup_link.click()
                time.sleep(3)  # 等待页面跳转
            else:
                logging.error("未找到 Sign up 链接")
                return False
            
            # 等待注册页面加载
            logging.info("等待注册页面加载完成...")
            time.sleep(5)
            
            # 查找邮箱输入框
            logging.info("正在查找邮箱输入框...")
            js_code = """
            return document.querySelector('#email') ||
                   document.querySelector('input.c8429dee9.c2ca7b14a') ||
                   document.querySelector('input[inputmode="email"][autocomplete="email"]') ||
                   document.querySelector('input[type="text"][name="email"][required]');
            """
            email_input = self.browser.page.run_js(js_code)
            
            if email_input:
                logging.info("找到邮箱输入框")
                time.sleep(1)
                
                # 清空输入框
                email_input.clear()
                time.sleep(0.5)
                
                # 输入邮箱
                email_input.input(test_email)
                logging.info("邮箱输入完成")
                time.sleep(1)

                # 处理验证码
                if not self.captcha_handler.verify_captcha(self.browser):
                    logging.error("验证码处理失败")
                    return False
                
                logging.info("验证码处理完成")
                time.sleep(1)

                return True
            
            logging.error("未找到邮箱输入框")
            return False

        except Exception as e:
            logging.error(f"测试过程出错: {str(e)}")
            return False
        finally:
            time.sleep(3)  # 等待一会儿以便查看结果
            self.browser.close()

def check_and_create_config():
    """
    检查并创建配置文件
    
    如果配置文件不存在，引导用户创建配置文件
    """
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    
    if os.path.exists(env_path):
        logging.info("配置文件已存在，将直接使用现有配置。")
        return
        
    logging.info("未检测到配置文件，开始引导配置...")
    
    # 准备配置模板
    config_template = """# ====== 临时邮箱配置 ======
# 临时邮箱用户名（不含@及后缀）
TEMP_MAIL={temp_mail}
# 临时邮箱后缀，默认使用 mailto.plus
TEMP_MAIL_EXT=@mailto.plus
# 临时邮箱 EPIN 验证码（用于API认证）
TEMP_MAIL_EPIN={temp_mail_epin}
# 临时邮箱 API 服务地址
TEMP_MAIL_API_URL=https://tempmail.plus/api

# ====== 域名配置 ======
# CloudFlare 路由配置的域名（用于邮箱验证）
DOMAIN={domain}

# ====== IMAP邮箱配置 ======
# 当 TEMP_MAIL=null 时使用以下 IMAP 配置
# IMAP 服务器地址
IMAP_SERVER={imap_server}
# IMAP 服务器端口（SSL）
IMAP_PORT=993
# IMAP 邮箱账号
IMAP_USER={imap_user}
# IMAP 邮箱密码
IMAP_PASS={imap_pass}
# IMAP 收件箱目录
IMAP_DIR=INBOX

# ====== 浏览器配置 ======
# 浏览器类型（目前支持 chrome）
BROWSER_TYPE=chrome
# 是否启用无头模式（true/false）
HEADLESS=true
# 浏览器 User-Agent 设置
BROWSER_USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36
# 浏览器窗口宽度
BROWSER_WIDTH=1920
# 浏览器窗口高度
BROWSER_HEIGHT=1080

# ====== 注册配置 ======
# Tavily API 注册页面 URL
REGISTER_URL=https://app.tavily.com/sign-up
"""
    
    # 引导用户输入配置
    print("\n=== 配置向导 ===")
    print("\n1. 请选择邮箱验证方式：")
    print("1) 使用临时邮箱（推荐）")
    print("2) 使用自己的IMAP邮箱")
    choice = input("请输入选择（1/2）: ").strip()
    
    config_values = {
        'temp_mail': 'null',
        'temp_mail_epin': '',
        'domain': '',
        'imap_server': '',
        'imap_user': '',
        'imap_pass': ''
    }
    
    if choice == '1':
        print("\n=== 临时邮箱配置 ===")
        config_values['temp_mail'] = input("请输入临时邮箱用户名（不含@及后缀）: ").strip()
        config_values['temp_mail_epin'] = input("请输入临时邮箱 EPIN 验证码: ").strip()
        config_values['domain'] = input("请输入 CloudFlare 路由配置的域名（格式：@your.domain）: ").strip()
    else:
        print("\n=== IMAP邮箱配置 ===")
        config_values['imap_server'] = input("请输入 IMAP 服务器地址: ").strip()
        config_values['imap_user'] = input("请输入 IMAP 邮箱账号: ").strip()
        config_values['imap_pass'] = input("请输入 IMAP 邮箱密码: ").strip()
    
    # 生成配置文件
    config_content = config_template.format(**config_values)
    
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        logging.info(f"配置文件已创建：{env_path}")
        print("\n配置文件已创建成功！您可以稍后在 .env 文件中修改这些配置。")
        
        # 等待用户确认
        input("\n按回车键继续...")
        
    except Exception as e:
        logging.error(f"创建配置文件失败: {str(e)}")
        sys.exit(1)

def main():
    """
    主程序入口
    """
    # 设置日志
    logger = setup_logger()
    logger.info("程序启动...")
    
    try:
        # 检查并创建配置文件
        check_and_create_config()
        
        # 加载配置
        config = Config()
        logger.info("配置加载成功")
        
        # 显示当前配置
        config.print_config()
        
        # 创建注册实例并运行
        register = TavilyAutoRegister()
        register.start()  # 运行完整的注册流程
        
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 