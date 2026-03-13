# Corporate Internal Management Framework

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Internal-red.svg)]()

**轻量级企业内部业务管理系统基础框架**

最初为酒店家具出口业务（FFE）设计，现作为通用内部管理系统的基础源代码进行维护与扩展。

---

## 特性

- 🔐 安全认证 - 登录保护、账号锁定、失败计数、密码强度验证
- 👥 用户管理 - CRUD操作、管理员权限控制、用户偏好设置
- ⚙️ 系统设置 - 可配置的上传限制、会话超时、审计日志、水印设置
- 🎨 多主题支持 - 5套预设主题，运行时即时切换
- 📱 响应式设计 - Bootstrap 5 + CSS变量主题系统
- 🛡️ 生产级安全 - SECRET_KEY强制检查、CSRF保护、会话安全
- 📝 完整日志 - 文件轮转日志、登录审计、操作记录

---

## 快速开始

```bash
# 1. 克隆项目
git clone <repo-url>
cd internal-project-management-system

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
internal-project-management-system/
├── app/
│   ├── __init__.py          # Flask 应用工厂
│   ├── models.py            # 数据模型
│   ├── routes/              # 路由层
│   ├── services/            # 服务层
│   ├── forms/               # WTForms 表单
│   ├── templates/           # Jinja2 模板
│   └── static/              # 静态资源
├── docs/                    # 开发文档
├── config.py                # 配置管理
├── run.py                   # 应用入口
└── requirements.txt         # 依赖清单
```

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端 | Python 3.10+ / Flask 2.3+ |
| 数据库 | SQLAlchemy / SQLite → PostgreSQL |
| 认证 | Flask-Login / Flask-WTF |
| 前端 | Jinja2 / Bootstrap 5 / CSS Variables |

---

## 配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | 应用密钥（生产≥48字符） | 自动生成 |
| `DATABASE_URL` | 数据库连接 | `sqlite:///instance/site.db` |
| `FLASK_ENV` | 环境 | `development` |
| `FLASK_PORT` | 端口 | `5001` |

---

## 文档

- [技术参考文档](docs/TECHNICAL.md) - 架构分层、开发规范、扩展指南

---

## 许可证

内部使用，禁止外传
