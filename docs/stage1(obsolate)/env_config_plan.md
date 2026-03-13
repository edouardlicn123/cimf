# 环境配置方案

## 概述

本项目使用 `config.env` 统一管理环境变量，通过 `python-dotenv` 库在应用启动时自动加载。

## 配置文件

| 文件 | 是否加入Git | 说明 |
|------|-------------|------|
| config.env.sample | ✅ 是 | 配置模板（带完整注释） |
| config.env | ❌ 否 | 实际配置（被 .gitignore 忽略） |

## 配置文件说明

### config.env.sample

模板文件，包含所有可用配置项及说明注释：

```env
# =============================================
# 项目基础配置
# =============================================
PROJECT_NAME=FFE 项目跟进系统
FLASK_ENV=development

# =============================================
# Flask 服务配置
# =============================================
FLASK_DEBUG=true
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

# =============================================
# 安全配置
# =============================================
# SECRET_KEY=  # 生产必填，至少48字符
# DATABASE_URL=sqlite:///instance/site.db

# =============================================
# 文件上传配置（未来扩展）
# =============================================
# UPLOAD_FOLDER=persistent_uploads
# MAX_CONTENT_LENGTH=16
# ALLOWED_EXTENSIONS=pdf,png,jpg,jpeg,gif,xlsx,docx,csv

# =============================================
# 会话与认证（未来扩展）
# =============================================
# SESSION_COOKIE_NAME=ffe_session
# PERMANENT_SESSION_LIFETIME=14

# =============================================
# 邮件配置（未来扩展）
# =============================================
# MAIL_SERVER=smtp.example.com
# MAIL_PORT=587
# MAIL_USERNAME=
# MAIL_PASSWORD=

# =============================================
# 日志配置（未来扩展）
# =============================================
# LOG_LEVEL=INFO
# LOG_RETENTION_DAYS=90
# ENABLE_AUDIT_LOG=true
```

## 使用方式

### 首次使用

```bash
# 方式1：使用 run.sh 菜单
./run.sh 6

# 方式2：手动复制
cp config.env.sample config.env
```

### 修改配置

编辑 `config.env` 文件，根据需要修改各项配置值。

### 配置加载

`run.py` 启动时自动加载：

```python
from dotenv import load_dotenv
load_dotenv('config.env')  # 加载 config.env 文件
```

## 配置分类

| 分类 | 状态 | 说明 |
|------|------|------|
| 基础配置 | ✅ 当前 | PROJECT_NAME, FLASK_ENV |
| Flask服务 | ✅ 当前 | FLASK_DEBUG, FLASK_HOST, FLASK_PORT |
| 安全配置 | ✅ 当前 | SECRET_KEY, DATABASE_URL |
| 文件上传 | 🔄 未来 | UPLOAD_FOLDER, MAX_CONTENT_LENGTH |
| 会话认证 | 🔄 未来 | SESSION_COOKIE_NAME, LOGIN_* |
| 邮件配置 | 🔄 未来 | MAIL_* |
| 云存储 | 🔄 未来 | AWS_S3_* |
| 缓存配置 | 🔄 未来 | CACHE_TYPE, REDIS_URL |
| 日志配置 | 🔄 未来 | LOG_LEVEL, LOG_RETENTION_DAYS |

## 涉及修改

| 文件 | 修改内容 |
|------|----------|
| config.env.sample | 新建：配置模板 |
| .gitignore | 添加 config.env 忽略规则 |
| run.py | 修改 load_dotenv('config.env') |
| run.sh | 添加选项 6：初始化环境变量文件 |

## 变更记录

- 2026-03-10：创建环境配置方案，统一使用 config.env
