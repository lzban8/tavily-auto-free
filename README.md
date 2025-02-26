# Tavily 自动注册工具

这是一个用于自动注册 Tavily 账户并获取 API 密钥的工具。

## 功能特性

- 自动化注册 Tavily 账户
- 自动处理邮箱验证
- 自动获取 API 密钥
- 完整的日志记录
- 可配置的重试机制
- 健壮的错误处理

## 安装要求

- Python 3.8+
- Chrome 浏览器
- ChromeDriver

## 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/tavily-auto.git
cd tavily-auto
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
```
然后编辑 `.env` 文件，填入你的配置信息。

## 使用方法

1. 确保已正确配置环境变量

2. 运行程序：
```bash
python -m src.tavily_register
```

## 配置说明

在 `.env` 文件中配置以下信息：

### 邮箱配置
- IMAP_SERVER: IMAP服务器地址
- IMAP_PORT: IMAP服务器端口
- IMAP_USER: 邮箱账号
- IMAP_PASS: 邮箱密码

### 浏览器配置
- HEADLESS: 是否使用无头模式
- USER_AGENT: 用户代理字符串
- WINDOW_WIDTH: 浏览器窗口宽度
- WINDOW_HEIGHT: 浏览器窗口高度

### 日志配置
- LOG_LEVEL: 日志级别
- LOG_FILE: 日志文件路径
- MAX_LOG_BYTES: 单个日志文件最大大小
- BACKUP_COUNT: 保留的日志文件数量

### 重试配置
- MAX_RETRIES: 最大重试次数
- RETRY_INTERVAL: 重试间隔（秒）
- TIMEOUT: 超时时间（秒）

## 注意事项

1. 请确保使用可靠的邮箱服务
2. 建议使用代理以避免IP被限制
3. 遵守Tavily的使用条款和政策
4. 定期更新ChromeDriver以匹配Chrome版本

## 许可证

MIT License

## 免责声明

本工具仅用于学习和研究目的。使用本工具时请遵守相关服务条款和法律法规。作者不对使用本工具造成的任何问题负责。 