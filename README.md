# Corporate Internal Management Framework

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Internal-red.svg)]()

**轻量级企业内部业务管理系统基础框架**

最初为酒店家具出口业务（FFE）设计，现作为通用内部管理系统的基础源代码进行维护与扩展。

---

## 特性

- 🔐 **安全认证** - 登录保护、账号锁定、失败计数、密码强度验证
- 👥 **用户管理** - CRUD操作、管理员权限控制、用户偏好设置
- ⚙️ **系统设置** - 可配置的上传限制、会话超时、审计日志、水印设置
- 🎨 **多主题支持** - 6套预设主题，运行时即时切换
- 📱 **响应式设计** - Bootstrap 5 + CSS变量主题系统
- 🛡️ **生产级安全** - SECRET_KEY强制检查、CSRF保护、会话安全
- 📝 **完整日志** - 文件轮转日志、登录审计、操作记录
- ⏰ **定时任务** - 统一Cron调度服务，支持时间同步、缓存清理等后台任务
- 🌐 **时间同步** - 自动与远程时间服务器同步，确保系统时间准确
- 💾 **缓存管理** - 智能缓存机制，支持手动/定时清理

---

## 快速开始

```bash
# 1. 克隆项目
git clone <repo-url>
cd cimf-v2

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python init_schema.py --with-data

# 5. 启动服务
python run.py
```

访问 `http://localhost:5001`

---

## 开发模式说明

在开发环境下运行 `python run.py` 时，Flask 使用 Werkzeug 开发服务器，默认启用 **自动重载 (Auto Reload)** 功能。

- 当检测到源代码文件变化时，服务器会自动重启
- 控制台会显示 "restart with stat" 信息，这是正常行为
- 如需禁用自动重载，可设置环境变量：
  ```bash
  FLASK_RUN_NO_RELOAD=1 python run.py
  ```

生产环境建议使用 gunicorn：
```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 run:app
```

---

## 项目结构

```
cimf-v2/
├── app/
│   ├── __init__.py              # Flask 应用工厂
│   ├── models/                  # 数据模型
│   │   ├── core/               # 核心模型（用户、设置、词汇表等）
│   │   └── node/               # Node 通用模型
│   ├── services/                # 服务层
│   │   ├── core/               # 核心服务
│   │   │   ├── cron_service.py           # Cron 调度服务
│   │   │   ├── settings_service.py        # 系统设置服务
│   │   │   ├── time_sync_service.py       # 时间同步服务
│   │   │   ├── time_service.py            # 时间服务入口
│   │   │   ├── tasks/                     # 定时任务
│   │   │   │   ├── base.py               # 任务基类
│   │   │   │   ├── time_sync_task.py      # 时间同步任务
│   │   │   │   └── cache_cleanup_task.py # 缓存清理任务
│   │   │   └── permission_service.py      # 权限服务
│   │   └── node/                # Node 服务
│   ├── modules/                 # 路由模块
│   │   ├── core/               # 核心模块
│   │   │   ├── admin/          # 管理后台
│   │   │   ├── cron/           # Cron 调度管理
│   │   │   ├── auth/           # 认证
│   │   │   ├── workspace/      # 工作区
│   │   │   ├── taxonomy/      # 词汇表
│   │   │   ├── time/           # 时间管理
│   │   │   └── export/         # 导出功能
│   │   └── nodes/              # Node 节点模块
│   ├── forms/                   # WTForms 表单
│   ├── templates/               # Jinja2 模板
│   └── static/                  # 静态资源
├── docs/                        # 开发文档
│   ├── 09_系统性能优化与时钟同步服务指引.md
│   ├── 10_统一Cron调度服务指引.md
│   └── progress.md              # 进度记录
├── config.py                    # 配置管理
├── run.py                      # 应用入口
└── requirements.txt           # 依赖清单
```

---

## 核心功能

### Cron 调度服务

统一的后台任务调度框架，支持：

| 任务 | 说明 | 默认间隔 |
|------|------|----------|
| 时间同步 | 与远程时间服务器同步 | 15 分钟 |
| 缓存清理 | 清理系统缓存 | 3 小时 |

管理入口：`/admin/cron`

### 系统设置

可配置项包括：

- **上传设置** - 文件大小限制、数量限制、允许的扩展名
- **会话安全** - 超时时间、登录失败次数、锁定时间
- **审计日志** - 启用/禁用、日志保留天数
- **水印设置** - 网页水印、导出水印、自定义内容、透明度
- **时间管理** - 同步服务器、同步间隔、时区、重试次数
- **Cron 任务** - 各任务的启用状态和执行间隔

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端 | Python 3.10+ / Flask 2.3+ |
| 数据库 | SQLAlchemy / SQLite → PostgreSQL |
| 认证 | Flask-Login / Flask-WTF |
| 前端 | Jinja2 / Bootstrap 5 / CSS Variables |
| 定时任务 | 自定义 CronService + threading |

---

## 配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | 应用密钥（生产≥48字符） | 自动生成 |
| `DATABASE_URL` | 数据库连接 | `sqlite:///instance/site.db` |
| `FLASK_ENV` | 环境 | `development` |
| `FLASK_PORT` | 端口 | `5001` |
| `DB_INIT_MODE` | 数据库初始化模式 | `none` |
| `DB_SEED_DATA` | 是否初始化种子数据 | `false` |

---

## 文档

- [技术参考文档](docs/TECHNICAL.md) - 架构分层、开发规范、扩展指南
- [09_系统性能优化与时钟同步服务指引](docs/09_系统性能优化与时钟同步服务指引.md) - 缓存优化、时间同步
- [10_统一Cron调度服务指引](docs/10_统一Cron调度服务指引.md) - 定时任务框架

---

## 许可证

内部使用，禁止外传
