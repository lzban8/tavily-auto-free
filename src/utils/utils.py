"""
通用工具模块

这个模块提供了一系列通用的工具函数，主要包括：
- 随机字符串生成
- 随机邮箱生成
- 随机密码生成
- 账号信息生成

提供了注册过程中需要的各种随机数据生成功能。
"""

import random
import string
from utils.logger import setup_logger
from config import Config

logger = setup_logger()

def generate_random_string(length=8):
    """
    生成随机字符串
    
    生成指定长度的随机字符串，包含大小写字母和数字
    
    Args:
        length (int): 要生成的字符串长度，默认为8
        
    Returns:
        str: 生成的随机字符串
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_email():
    """
    生成随机邮箱
    
    使用随机字符串作为用户名，配置的域名作为邮箱域名
    
    Returns:
        str: 生成的随机邮箱地址
    """
    config = Config()
    username = generate_random_string(8)
    domain = config.DOMAIN.strip('@')  # 移除可能存在的@前缀
    return f"{username}@{domain}"

def generate_password():
    """
    生成随机密码
    
    生成符合以下要求的随机密码：
    - 包含大小写字母
    - 包含数字
    - 包含特殊字符
    - 长度为12位
    - 每种字符至少出现一次
    
    Returns:
        str: 生成的随机密码
    """
    # 生成包含大小写字母、数字和特殊字符的密码
    length = 12
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "@#$%"  # 只使用部分特殊字符
    
    # 确保密码包含所有类型的字符
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special)
    ]
    
    # 添加剩余的随机字符
    remaining_length = length - len(password)
    all_chars = lowercase + uppercase + digits + special
    password.extend(random.choice(all_chars) for _ in range(remaining_length))
    
    # 打乱密码字符顺序
    random.shuffle(password)
    return ''.join(password)

def generate_account_info(domain):
    """
    生成账号信息
    
    生成包含邮箱和密码的账号信息字典
    
    Args:
        domain (str): 邮箱域名
        
    Returns:
        dict: 包含邮箱和密码的账号信息字典
    """
    email = generate_email()
    password = generate_password()
    
    return {
        'email': email,
        'password': password
    } 