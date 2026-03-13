# Node 模块建立指引

本文档提供创建新 Node 节点类型的通用指引，客户管理模块作为参考示例。

---

## 一、概述

Node 系统是一个灵活的节点类型管理框架，允许通过管理界面创建各种业务节点类型，每个节点类型可以配置不同的字段。

### 1.1 目录结构规范

```
app/
├── models/
│   ├── core/                    # 共享模型
│   └── node/                    # Node 专用模型
│       ├── __init__.py
│       ├── node_type.py         # 节点类型模型
│       └── node.py              # 节点数据模型
├── services/
│   ├── core/                    # 共享服务
│   └── node/                    # Node 专用服务
│       ├── __init__.py
│       ├── node_type_service.py
│       ├── node_service.py
│       └── {node_slug}/         # 如 customer/
│           ├── __init__.py
│           └── {node_slug}_service.py
├── modules/
│   ├── core/                    # 共享模块
│   │   ├── node/               # 核心管理模块
│   │   │   ├── routes.py       # Dashboard、节点类型管理路由
│   │   │   └── service.py      # NodeTypeService
│   │   └── ...
│   └── nodes/                  # 各 node 类型（具体业务）
│       ├── __init__.py
│       └── {node_slug}/         # 如 customer/
│           ├── __init__.py     # NODE_TYPE_CONFIG
│           ├── routes.py       # CRUD 路由
│           └── forms.py        # 表单
└── templates/
    ├── core/
    │   └── node/                # 核心管理模板
    │       ├── frame_node.html
    │       ├── dashboard.html
    │       ├── node_type_admin.html
    │       └── node_type_settings.html
    └── nodes/                   # 各节点类型模板
        └── {node_slug}/         # 如 customer/
            ├── list.html
            ├── view.html
            └── edit.html
```

### 1.2 目录职责划分

| 目录 | 职责 |
|------|------|
| `core/node/` | 核心管理：Dashboard、节点类型管理、启用/禁用/删除、设置 |
| `modules/nodes/{node_slug}/` | 节点业务：CRUD 路由、表单、配置 |
| `templates/core/node/` | 核心管理模板 |
| `templates/nodes/{node_slug}/` | 节点类型模板 |

### 1.3 路由设计

| 路径 | 模块 | 说明 |
|------|------|------|
| `/nodes` | core/node | Dashboard - 所有节点类型入口 |
| `/nodes/admin/node-types` | core/node | 节点类型管理 |
| `/nodes/{node_slug}` | nodes/{node_slug} | 数据 CRUD |

### 1.4 命名规范

- **节点类型机器名**：使用小写字母和下划线，如 `customer`、`project`、`order`
- **目录名**：与机器名一致，如 `customer/`
- **类名**：使用 PascalCase，如 `CustomerService`、`CustomerForm`
- **表名**：`{node_slug}_fields`，如 `customer_fields`

### 1.5 节点类型配置文件

每个节点类型必须有一个独立的配置文件：

```python
# app/modules/nodes/{node_slug}/__init__.py
"""节点配置文件"""

from app.modules.nodes.{node_slug}.routes import {Node}BP

NODE_TYPE_CONFIG = {
    'slug': '{node_slug}',
    'name': '{节点名称}',
    'description': '{描述}',
    
    'files': {
        'model': 'app/models/node/{node_slug}.py',
        'service': 'app/services/node/{node_slug}/{node_slug}_service.py',
        'routes': 'app/modules/nodes/{node_slug}/routes.py',
        'forms': 'app/modules/nodes/{node_slug}/forms.py',
        'templates': 'app/templates/nodes/{node_slug}/',
    },
    
    'tables': {
        'main': 'nodes',
        'fields': '{node_slug}_fields',
    },
    
    'fields': [
        # 字段配置...
    ],
    
    'enabled': True,
}

def get_config():
    return NODE_TYPE_CONFIG
```

### 1.6 系统预定义字段类型

创建 Node 类型时，除非需要自定义字段类型，否则**必须**从以下系统预定义字段类型中选择：

| 机器名 | 标签 | 内部属性 |
|--------|------|----------|
| string | 单行文本 | value |
| string_long | 多行纯文本 | value |
| text | 带格式文本 | value, format |
| text_long | 带格式长文本 | value, format |
| text_with_summary | 含摘要文本 | value, summary, format |
| boolean | 布尔值 | value |
| integer | 整数 | value |
| decimal | 精确小数 | value |
| float | 浮点数 | value |
| entity_reference | 关联引用 | target_id, target_type |
| file | 文件 | target_id, display, description |
| image | 图片 | target_id, alt, title, width, height |
| link | 链接 | uri, title, options |
| email | 邮箱 | value |
| telephone | 电话 | value |
| datetime | 日期时间 | value |
| timestamp | 时间戳 | value |
| geolocation | 地理位置 | lat, lng, address |
| color | 颜色选择器 | color_code, opacity |
| ai_tags | 智能标签 | term_id, confidence_score |
| identity | 证件识别码 | id_number, id_type, is_verified |
| masked | 隐私脱敏字段 | raw_value, display_value, permission_level |
| biometric | 生物特征引用 | feature_vector, type, version |
| address | 标准地址 | province, city, district, street, house_number, grid_id |
| gis | 地理围栏 | point, spatial_ref |

**重要**：
- 系统字段类型位于 `app/modules/core/fields/`
- 如需创建自定义字段类型，请参考 `app/modules/core/fields/base.py` 中的 `BaseField` 基类
- 自定义字段类型文件应放在 `app/modules/fields/` 目录下

---

## 二、核心模块（已实现）

### 2.1 模型层

#### 2.1.1 节点类型模型 `app/models/node/node_type.py`

```python
class NodeType(db.Model):
    """节点类型"""
    __tablename__ = 'node_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(500))
    fields_config = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### 2.1.2 节点主表模型 `app/models/node/node.py`

```python
class Node(db.Model):
    """节点主表 - 所有节点类型的公共字段"""
    __tablename__ = 'nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    node_type_id = db.Column(db.Integer, db.ForeignKey('node_types.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    node_type = db.relationship('NodeType', backref='nodes')
    creator = db.relationship('User', foreign_keys=[created_by])
    updater = db.relationship('User', foreign_keys=[updated_by])
```

### 2.2 服务层

#### 2.2.1 节点类型服务 `app/services/node/node_type_service.py`

已实现以下方法：
- `get_all()` - 获取所有已启用的节点类型
- `get_all_including_inactive()` - 获取所有节点类型（含禁用的）
- `get_by_id(id)` - 根据 ID 获取
- `get_by_slug(slug)` - 根据 slug 获取
- `get_by_slug_including_inactive(slug)` - 获取（含禁用）
- `create(data)` - 创建
- `update(id, data)` - 更新
- `delete(id)` - 删除（软删除）
- `enable(id)` - 启用
- `disable(id)` - 禁用
- `get_node_count(id)` - 获取节点数量
- `init_default_node_types()` - 初始化预置节点类型

### 2.3 核心路由

| 路径 | 函数 | 说明 |
|------|------|------|
| `/nodes` | `node.dashboard` | 事务总览 |
| `/nodes/admin/node-types` | `node.node_type_admin` | 节点类型管理 |
| `/nodes/admin/node-types/<id>/enable` | `node.node_type_enable` | 启用 |
| `/nodes/admin/node-types/<id>/disable` | `node.node_type_disable` | 禁用 |
| `/nodes/admin/node-types/<id>/delete` | `node.node_type_delete` | 删除 |
| `/nodes/admin/node-types/<id>/settings` | `node.node_type_settings` | 设置 |

### 2.4 框架入口

- **节点类型管理**：使用 `frame_structure.html` 框架（与词汇表管理并列）
- **数据管理**：使用 `frame_node.html` 框架

在 `frame_node.html` 侧边栏添加节点入口：
```html
<li class="nav-item">
  <a class="nav-link ... {{ 'active' if active_section == '{node_slug}' else '' }}" 
     href="{{ url_for('{node_slug}.index') }}">
    <i class="bi bi-..."></i>
    {节点名称}
  </a>
</li>
```

---

## 三、创建新节点类型步骤

### 步骤 1：创建模型文件

`app/models/node/{node_slug}.py`：

```python
# {节点名称}字段模型
from datetime import datetime
from app import db

class {Node}Fields(db.Model):
    """{节点名称}字段表"""
    __tablename__ = '{node_slug}_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'), nullable=False, unique=True)
    
    # 字段定义...
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    node = db.relationship('Node', backref='fields', uselist=False)
```

### 步骤 2：创建服务文件

`app/services/node/{node_slug}/{node_slug}_service.py`：

```python
# {节点名称}服务
from app.models.node import Node, NodeType
from app.models.node.{node_slug} import {Node}Fields
from app.services.node.node_type_service import NodeTypeService
from app import db

class {Node}Service:
    """{节点名称}专用服务"""
    
    NODE_TYPE_SLUG = '{node_slug}'
    
    @staticmethod
    def get_node_type():
        return NodeTypeService.get_by_slug({Node}Service.NODE_TYPE_SLUG)
    
    @staticmethod
    def get_list(page=1, per_page=20):
        node_type = {Node}Service.get_node_type()
        if not node_type:
            return []
        return Node.query.filter_by(node_type_id=node_type.id).paginate(page=page, per_page=per_page)
    
    @staticmethod
    def get_by_id(id):
        node = Node.query.get(id)
        if not node:
            return None
        fields = {Node}Fields.query.filter_by(node_id=id).first()
        return {'node': node, 'fields': fields}
    
    @staticmethod
    def create(data, user_id):
        node_type = {Node}Service.get_node_type()
        
        node = Node(
            node_type_id=node_type.id,
            created_by=user_id,
            updated_by=user_id
        )
        db.session.add(node)
        db.session.flush()
        
        fields = {Node}Fields(
            node_id=node.id,
            # 字段映射...
        )
        db.session.add(fields)
        db.session.commit()
        
        return node
    
    @staticmethod
    def update(id, data, user_id):
        node = Node.query.get(id)
        node.updated_by = user_id
        
        fields = {Node}Fields.query.filter_by(node_id=id).first()
        if fields:
            for key, value in data.items():
                if hasattr(fields, key):
                    setattr(fields, key, value)
        
        db.session.commit()
        return node
    
    @staticmethod
    def delete(id):
        fields = {Node}Fields.query.filter_by(node_id=id).first()
        if fields:
            db.session.delete(fields)
        
        node = Node.query.get(id)
        if node:
            db.session.delete(node)
        
        db.session.commit()
```

### 步骤 3：创建服务入口

`app/services/node/{node_slug}/__init__.py`：

```python
from app.services.node.{node_slug}.{node_slug}_service import {Node}Service
```

### 步骤 4：创建路由文件

`app/modules/nodes/{node_slug}/routes.py`：

```python
# {节点名称}路由
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services.node.{node_slug} import {Node}Service

{NODE}_bp = Blueprint('{node_slug}', __name__, url_prefix='/nodes/{node_slug}')

@{NODE}_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    pagination = {Node}Service.get_list(page=page)
    return render_template('nodes/{node_slug}/list.html', 
                         items=pagination.items,
                         pagination=pagination)

@{NODE}_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    from app.modules.nodes.{node_slug}.forms import {Node}Form
    
    form = {Node}Form()
    
    if form.validate_on_submit():
        data = {
            # 字段映射...
        }
        {Node}Service.create(data, current_user.id)
        flash('{节点名称}创建成功', 'success')
        return redirect(url_for('{node_slug}.index'))
    
    return render_template('nodes/{node_slug}/edit.html', form=form, action='create')

@{NODE}_bp.route('/<int:id>')
@login_required
def view(id):
    result = {Node}Service.get_by_id(id)
    if not result:
        flash('{节点名称}不存在', 'danger')
        return redirect(url_for('{node_slug}.index'))
    return render_template('nodes/{node_slug}/view.html', node=result['node'], fields=result['fields'])

@{NODE}_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    from app.modules.nodes.{node_slug}.forms import {Node}Form
    
    result = {Node}Service.get_by_id(id)
    if not result:
        flash('{节点名称}不存在', 'danger')
        return redirect(url_for('{node_slug}.index'))
    
    form = {Node}Form(data=result['fields'].__dict__ if result['fields'] else {})
    
    if form.validate_on_submit():
        data = {
            # 字段映射...
        }
        {Node}Service.update(id, data, current_user.id)
        flash('{节点名称}更新成功', 'success')
        return redirect(url_for('{node_slug}.view', id=id))
    
    return render_template('nodes/{node_slug}/edit.html', form=form, action='edit', node=result['node'], fields=result['fields'])

@{NODE}_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    {Node}Service.delete(id)
    flash('{节点名称}已删除', 'success')
    return redirect(url_for('{node_slug}.index'))
```

### 步骤 5：创建表单文件

`app/modules/nodes/{node_slug}/forms.py`：

```python
# {节点名称}表单
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional

class {Node}Form(FlaskForm):
    # 字段定义...
    submit = SubmitField('保存', render_kw={"class": "btn btn-primary"})
```

### 步骤 6：创建模板文件

创建以下模板：
- `app/templates/nodes/{node_slug}/list.html` - 列表页
- `app/templates/nodes/{node_slug}/view.html` - 详情页
- `app/templates/nodes/{node_slug}/edit.html` - 新建/编辑页

模板应继承 `core/frame_node.html`：

```html
{% extends "core/frame_node.html" %}

{% set active_section = '{node_slug}' %}

{% block admin_title %}
  {节点名称}管理
{% endblock %}
```

### 步骤 7：注册蓝图

在 `app/routes/__init__.py` 中注册：

```python
from app.modules.nodes.{node_slug} import {NODE}_bp

# 注册蓝图
app.register_blueprint({NODE}_bp, url_prefix='/nodes/{node_slug}')
```

### 步骤 8：添加侧边栏入口

在 `app/templates/core/frame_node.html` 中添加链接。

---

## 四、参考示例

客户管理模块作为完整参考示例，请参见 [05_客户信息范例.md](./05_客户信息范例.md)。

### 4.1 客户模型示例

`app/models/node/customer.py` - 客户字段模型

### 4.2 客户服务示例

`app/services/node/customer/customer_service.py` - CustomerService

### 4.3 客户路由示例

`app/modules/nodes/customer/routes.py` - 客户 CRUD 路由

### 4.4 客户表单示例

`app/modules/nodes/customer/forms.py` - CustomerForm

### 4.5 客户模板示例

- `app/templates/nodes/customer/list.html`
- `app/templates/nodes/customer/view.html`
- `app/templates/nodes/customer/edit.html`

---

## 五、权限配置

每个节点类型应配置以下权限：

| 权限 | 说明 |
|------|------|
| `node.{node_slug}.create` | 创建 |
| `node.{node_slug}.read` | 查看 |
| `node.{node_slug}.update` | 编辑 |
| `node.{node_slug}.delete` | 删除 |

---

## 六、版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-03-13 | 初始版本 |
