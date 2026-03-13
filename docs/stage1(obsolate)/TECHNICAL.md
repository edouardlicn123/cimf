# 技术参考文档

本文档为开发团队提供完整的技术架构说明、开发规范和扩展指南。

---

## 1. 项目结构

```
internal-project-management-system/
├── app/
│   ├── __init__.py              # Flask 应用工厂
│   ├── models.py                # 数据模型 (User, SystemSetting)
│   ├── routes/
│   │   ├── __init__.py          # 蓝图注册入口
│   │   ├── auth.py              # 认证模块 (登录/登出)
│   │   ├── main.py              # 主页面 (仪表盘/设置)
│   │   ├── admin.py             # 后台管理
│   │   ├── calculator.py        # 计算器模块 (预留)
│   │   └── project.py           # 项目模块 (预留)
│   ├── services/
│   │   ├── auth_service.py      # 认证业务逻辑
│   │   ├── user_service.py      # 用户管理业务逻辑
│   │   ├── settings_service.py  # 系统设置业务逻辑
│   │   └── calc/                # 计算服务
│   ├── forms/
│   │   ├── auth_forms.py        # 认证表单
│   │   ├── admin_forms.py       # 管理表单
│   │   └── settings_forms.py    # 设置表单
│   ├── templates/               # Jinja2 模板
│   │   ├── base.html            # 基础模板
│   │   ├── auth/                # 认证模板
│   │   ├── main/                # 主页面模板
│   │   └── admin/               # 管理模板
│   └── static/
│       ├── css/                 # 样式文件
│       │   ├── base.css         # 基础样式
│       │   ├── custom.css       # 自定义样式
│       │   ├── frame.css        # 框架样式
│       │   └── themes/          # 主题文件
│       └── js/                  # JavaScript 文件
├── docs/                        # 开发文档
├── config.py                    # 配置管理
├── run.py                       # 应用入口
└── requirements.txt             # 依赖清单
```

---

## 2. 架构分层

### 2.1 路由层 (app/routes/)

薄路由设计原则：**只负责接收请求、简单校验、调用服务、返回响应**

```
路由函数 = 接收请求 → 参数校验 → 调用服务层 → 渲染响应
```

禁止在路由层直接进行：
- 数据库查询
- 复杂业务计算
- 文件处理逻辑

### 2.2 服务层 (app/services/)

核心业务逻辑封装，包含：
- 数据库操作
- 业务规则处理
- 计算逻辑
- 数据转换

### 2.3 模型层 (app/models.py)

使用 SQLAlchemy 定义：
- `User` - 用户实体（支持登录、权限、偏好）
- `SystemSetting` - 系统配置（键值对存储）

### 2.4 表单层 (app/forms/)

使用 Flask-WTF 定义表单类，统一处理：
- 字段验证
- CSRF 保护
- HTML 属性渲染

---

## 3. 开发规范

### 3.1 文件头部注释

所有新增/修改的文件必须在顶部添加标准注释块：

```python
# 文件路径：app/routes/xxx.py
# 更新日期：2026-02-17
# 功能说明：模块功能描述
```

```html
{# 文件路径：app/templates/xxx.html #}
{# 更新日期：2026-02-17 #}
{# 功能说明：页面功能描述 #}
```

### 3.2 前后端分离

严格遵循分层架构：

```python
# 路由层
@bp.route('/page')
def page():
    result = XxxService.process(data)  # 调用服务层
    return render_template('page.html', result=result)

# 服务层
class XxxService:
    @staticmethod
    def process(data):
        # 业务逻辑
        return result
```

### 3.3 模板规范

- Jinja2 注释使用 `{# ... #}`，禁止使用 `<!-- ... -->`
- 样式类名参考 `docs/9css-elements-reference.md`
- 禁止随意发明新 class，优先复用已有定义

### 3.4 路由规范

- 所有路由必须显式声明 `methods=['GET']` 或 `methods=['GET', 'POST']`
- 新建蓝图时添加 `@bp.before_request @login_required` 全局登录保护

### 3.5 安全规范

- 用户输入必须 `.strip()` 处理
- 生产环境 `SECRET_KEY` 长度必须 ≥48 字符
- 日志统一使用 `app.logger`，禁止直接 `print()`

---

## 4. CSS 规范

### 4.1 主题系统

使用 CSS 变量实现多主题切换：

```css
:root {
    --primary: #0d6efd;
    --success: #198754;
    --danger: #dc3545;
    /* ... */
}
```

已内置主题：`default`, `dopamine`, `macaron`, `teal`, `uniklo`

### 4.2 通用样式类

| 类名 | 用途 |
|------|------|
| `.welcome-title` | 欢迎/主标题 |
| `.settings-title` | 设置/表单标题 |
| `.dashboard-cards` | 仪表盘卡片容器 |
| `.card-entry` | 单卡片 |
| `.card-btn` | 通用按钮 |
| `.primary-btn` | 主按钮 |

详见 `docs/9css-elements-reference.md`

---

## 5. 扩展指南

### 5.1 新增业务模块

1. **创建服务层** `app/services/xxx_service.py`

```python
from app import db
from app.models import XxxModel

class XxxService:
    @staticmethod
    def get_items():
        return XxxModel.query.all()
    
    @staticmethod
    def create_item(data):
        item = XxxModel(**data)
        db.session.add(item)
        db.session.commit()
        return item
```

2. **创建路由层** `app/routes/xxx.py`

```python
from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('xxx', __name__)

@bp.before_request
@login_required
def require_login():
    pass

@bp.route('/xxx')
def index():
    items = XxxService.get_items()
    return render_template('xxx/index.html', items=items)
```

3. **注册蓝图** 在 `app/routes/__init__.py` 添加：

```python
from .xxx import bp as xxx_bp
# ...
app.register_blueprint(xxx_bp, url_prefix='/xxx')
```

### 5.2 新增数据模型

在 `app/models.py` 添加：

```python
class XxxModel(db.Model):
    __tablename__ = 'xxx'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    # ...
```

---

## 6. 环境配置

### 6.1 环境变量

| 变量 | 说明 | 必填 | 默认值 |
|------|------|------|--------|
| `SECRET_KEY` | 应用密钥 | 生产环境 | 自动生成 |
| `DATABASE_URL` | 数据库连接 | 否 | SQLite |
| `FLASK_ENV` | 运行环境 | 否 | development |
| `FLASK_DEBUG` | 调试模式 | 否 | 随 ENV |
| `FLASK_HOST` | 监听地址 | 否 | 0.0.0.0 |
| `FLASK_PORT` | 监听端口 | 否 | 5001 |

### 6.2 生产环境检查

`run.py` 启动时会强制检查：
- `SECRET_KEY` 长度 ≥48
- `DEBUG` 必须为 `false`
- 建议使用 `gunicorn` 或 `uvicorn` 部署

---

## 7. 数据库

### 7.1 初始化

```bash
# 交互式初始化（推荐）
python run.py

# 或命令行初始化
python init_schema.py --with-data
```

### 7.2 模型变更

开发环境：删除 `instance/site.db` 重新初始化

生产环境：使用 Flask-Migrate
```bash
flask db migrate -m "description"
flask db upgrade
```

---

## 8. 日志

日志文件位于 `logs/ffe.log`，使用轮转机制：
- 单文件最大 10MB
- 保留 5 个备份

日志格式：
```
%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s
```

---

## 9. 依赖清单

```
Flask>=2.3
Flask-SQLAlchemy>=3.0
Flask-Login>=0.6
Flask-WTF>=1.2
Werkzeug>=2.3
python-dotenv>=1.0
```

详见 `requirements.txt`

---

## 10. 常用命令

```bash
# 开发启动
python run.py

# 数据库初始化
python init_schema.py --with-data

# 安装依赖
pip install -r requirements.txt
```

---

*本文档为内部开发参考，请勿外传*
