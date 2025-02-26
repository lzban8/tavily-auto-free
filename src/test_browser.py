from src.browser_manager import BrowserManager
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

def test_browser():
    """测试浏览器基本功能"""
    config = {
        'headless': False,
        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'proxy': None  # 如果需要代理，在这里设置
    }
    
    browser = BrowserManager(config)
    
    try:
        # 1. 测试导航到注册页面
        print("测试1: 导航到注册页面")
        browser.navigate_to("https://app.tavily.com/signup")
        time.sleep(5)  # 增加等待时间
        
        # 保存页面源码以分析结构
        print("\n保存页面源码...")
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(browser.page.html)
        print("已保存页面源码到 page_source.html")
        
        # 保存初始页面截图
        print("\n保存初始页面截图...")
        browser.save_screenshot('tavily_initial.png')
        
        # 2. 测试输入邮箱
        print("\n测试2: 输入邮箱")
        # 更新邮箱输入框选择器以匹配实际元素
        email_selectors = [
            'input@id="username"',  # 使用id选择器
            'input@name="username"',  # 使用name选择器
            'input@class="input cec61d1fe c54babdaf"',  # 使用class选择器
            'input@inputmode="email"',  # 使用inputmode选择器
            'input@autocomplete="email"'  # 使用autocomplete选择器
        ]
        
        email_input = None
        for selector in email_selectors:
            print(f"尝试选择器: {selector}")
            email_input = browser.find_element('xpath', selector)
            if email_input:
                print(f"✓ 成功找到邮箱输入框，使用选择器: {selector}")
                break
        
        if email_input and browser.input_text(email_input, "test@example.com"):
            print("✓ 成功输入邮箱")
        else:
            print("✗ 输入邮箱失败")
            # 如果失败，保存当前页面源码和截图
            browser.save_screenshot('email_input_failed.png')
            with open('email_input_failed.html', 'w', encoding='utf-8') as f:
                f.write(browser.page.html)
            print("已保存失败时的页面源码到 email_input_failed.html")
        
        # 3. 等待并输入验证码
        print("\n测试3: 等待验证码输入框")
        time.sleep(3)  # 等待验证码输入框出现
        
        verification_selectors = [
            'input@type="text"',
            'input@placeholder*="verification"',
            'input@placeholder*="code"',
            'input@name="code"'
        ]
        
        verification_input = None
        for selector in verification_selectors:
            verification_input = browser.find_element('xpath', selector)
            if verification_input:
                print(f"✓ 成功找到验证码输入框，使用选择器: {selector}")
                break
                
        if verification_input:
            print("找到验证码输入框，请手动输入验证码")
            browser.save_screenshot('tavily_verification.png')
        else:
            print("✗ 未找到验证码输入框")
            
        # 4. 查找并点击 Continue 按钮
        print("\n测试4: 点击Continue按钮")
        continue_selectors = [
            'button@text="Continue"',
            'button@text*="continue"',
            'button@type="submit"'
        ]
        
        continue_button = None
        for selector in continue_selectors:
            continue_button = browser.find_element('xpath', selector)
            if continue_button:
                print(f"✓ 成功找到Continue按钮，使用选择器: {selector}")
                break
        
        if continue_button and browser.click_element(continue_button):
            print("✓ 成功点击Continue按钮")
        else:
            print("✗ 点击Continue按钮失败")
            
        time.sleep(3)  # 等待页面响应
        
        # 5. 测试输入密码（如果到达密码页面）
        print("\n测试5: 输入密码")
        password_selectors = [
            'input@type="password"',
            'input@name="password"',
            'input@placeholder*="password"'
        ]
        
        password_input = None
        for selector in password_selectors:
            password_input = browser.find_element('xpath', selector)
            if password_input:
                print(f"✓ 成功找到密码输入框，使用选择器: {selector}")
                break
        
        if password_input and browser.input_text(password_input, "YourTestPassword123!"):
            print("✓ 成功输入密码")
        else:
            print("✗ 输入密码失败")
            
        # 保存最终页面截图
        print("\n保存最终页面截图...")
        browser.save_screenshot('tavily_final.png')
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        # 发生错误时也保存截图和页面源码
        browser.save_screenshot('tavily_error.png')
        with open('error_page_source.html', 'w', encoding='utf-8') as f:
            f.write(browser.page.html)
        print("已保存错误页面源码到 error_page_source.html")
    finally:
        # 6. 测试关闭浏览器
        print("\n测试6: 关闭浏览器")
        browser.close()
        print("✓ 浏览器已关闭")

if __name__ == "__main__":
    test_browser() 