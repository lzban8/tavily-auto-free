# Tavily API Key 自动注册工具

这是一个用于自动注册 Tavily API Key 的 Python 工具。它使用 DrissionPage 进行浏览器自动化，支持验证码识别，并能自动保存账号信息。

## 作者
- GitHub: [FeiGod](https://github.com/FeiGod)

## 功能特点

- 自动生成随机邮箱和密码
- 自动填写注册表单
- 自动识别和处理验证码
- 自动获取 API Key
- 支持无头模式运行
- 支持保存账号信息到 CSV 文件（支持中文）
- 完整的日志记录
- 可配置的浏览器参数

## 环境要求

- Python 3.9+
- Chrome 浏览器

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

在项目根目录创建 `.env` 文件，配置以下参数：

```env
# ====== 临时邮箱配置 ======
# 临时邮箱用户名（不含@及后缀）
TEMP_MAIL=your_temp_mail
# 临时邮箱后缀，默认使用 mailto.plus
TEMP_MAIL_EXT=@mailto.plus
# 临时邮箱 EPIN 验证码（用于API认证）
TEMP_MAIL_EPIN=your_epin
# 临时邮箱 API 服务地址
TEMP_MAIL_API_URL=https://tempmail.plus/api

# ====== 域名配置 ======
# CloudFlare 路由配置的域名（用于邮箱验证）
DOMAIN=@your.domain

# ====== IMAP邮箱配置 ======
# 当 TEMP_MAIL=null 时使用以下 IMAP 配置
# IMAP 服务器地址
IMAP_SERVER=imap.example.com
# IMAP 服务器端口（SSL）
IMAP_PORT=993
# IMAP 邮箱账号
IMAP_USER=your_email@example.com
# IMAP 邮箱密码
IMAP_PASS=your_password
# IMAP 收件箱目录
IMAP_DIR=INBOX

# ====== 浏览器配置 ======
# 浏览器类型（目前支持 chrome）
BROWSER_TYPE=chrome
# 是否启用无头模式（true/false）
HEADLESS=true
# 浏览器 User-Agent 设置
BROWSER_USER_AGENT=your_user_agent
# 浏览器窗口宽度
BROWSER_WIDTH=1920
# 浏览器窗口高度
BROWSER_HEIGHT=1080

# ====== 注册配置 ======
# Tavily API 注册页面 URL
REGISTER_URL=https://app.tavily.com/sign-up
```

### 配置项说明

1. **临时邮箱配置**
   - `TEMP_MAIL`: 临时邮箱用户名，不包含@及后缀
   - `TEMP_MAIL_EXT`: 临时邮箱后缀，默认为 @mailto.plus
   - `TEMP_MAIL_EPIN`: 临时邮箱 EPIN 验证码，用于 API 认证
   - `TEMP_MAIL_API_URL`: 临时邮箱 API 服务地址

2. **域名配置**
   - `DOMAIN`: CloudFlare 路由配置的域名，用于邮箱验证

3. **IMAP邮箱配置**（当 TEMP_MAIL=null 时使用）
   - `IMAP_SERVER`: IMAP 服务器地址
   - `IMAP_PORT`: IMAP 服务器端口，默认 993（SSL）
   - `IMAP_USER`: IMAP 邮箱账号
   - `IMAP_PASS`: IMAP 邮箱密码
   - `IMAP_DIR`: IMAP 收件箱目录，默认为 INBOX

4. **浏览器配置**
   - `BROWSER_TYPE`: 浏览器类型，目前支持 chrome
   - `HEADLESS`: 是否启用无头模式，true/false
   - `BROWSER_USER_AGENT`: 浏览器 User-Agent 设置
   - `BROWSER_WIDTH`: 浏览器窗口宽度，默认 1920
   - `BROWSER_HEIGHT`: 浏览器窗口高度，默认 1080

5. **注册配置**
   - `REGISTER_URL`: Tavily API 注册页面地址

## 项目结构

```
tavily-auto-free/
├── README.md
├── requirements.txt
├── .env
├── src/
│   ├── __init__.py
│   ├── tavily_auto.py          # 主程序
│   ├── config.py               # 配置管理
│   ├── core/
│   │   ├── __init__.py
│   │   ├── browser_utils.py    # 浏览器工具
│   │   ├── captcha_handler.py  # 验证码处理
│   │   └── email_verify.py     # 邮箱验证
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # 日志工具
│       └── utils.py            # 通用工具
└── screenshots/                 # 验证码截图保存目录
```

## 使用方法

1. 配置环境：
   ```bash
   # 克隆项目
   git clone https://github.com/your-username/tavily-auto-free.git
   cd tavily-auto-free
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 配置 .env 文件
   cp .env.example .env
   # 编辑 .env 文件，填入您的配置
   ```

2. 运行程序：
   ```bash
   python src/tavily_auto.py
   ```

## 输出说明

程序运行后会在当前目录生成 `accounts.csv` 文件，包含以下信息：
- 邮箱
- 密码
- API密钥
- 创建时间

## 注意事项

1. 确保 Chrome 浏览器已安装
2. 确保网络连接正常
3. 建议使用无头模式运行，可以提高效率
4. 验证码识别可能需要多次尝试
5. 账号信息会自动保存，请妥善保管

## 常见问题

1. 浏览器启动失败
   - 检查 Chrome 是否正确安装
   - 检查 DrissionPage 版本是否兼容

2. 验证码识别失败
   - 程序会自动重试
   - 可以调整等待时间

3. CSV 文件中文乱码
   - 文件使用 UTF-8 with BOM 编码
   - 使用支持 UTF-8 的编辑器打开

## 更新日志

### v1.0.0 (2024-02-28)
- 初始版本发布
- 支持自动注册
- 支持验证码识别
- 支持账号信息保存

## 许可证

MIT License 