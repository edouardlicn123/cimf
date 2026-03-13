# Node/Taxonomy 系统实现计划

> ⚠️ **注意**：本文件已被拆分，具体内容移至以下文件：
> - `01_总计划.md` - 概述和执行顺序
> - `02_现有功能迁移.md` - 现有功能迁移计划
> - `03_taxonomy模块.md` - Taxonomy 模块设计
> - `04_字段模块.md` - 字段模块设计
> - `05_客户信息范例.md` - 客户信息实现范例

---

## 一、系统概述

本系统用于在现有系统之上构建可自定义的数据模型，类似于 Drupal 的字段系统。

### 核心概念

| 概念 | 说明 |
|------|------|
| **Node（节点）** | 记录客户信息、项目信息等内容实体 |
| **NodeType（节点类型）** | 定义节点的字段结构 |
| **FieldType（字段类型）** | 预定义的字段类型（文本、数字、日期等） |
| **Taxonomy（词汇表）** | 下拉选项集合（如性别男/女） |
| **附加功能** | 节点类型管理、词汇表管理、数据分析等 |

---

## 二、模块化架构设计

### 2.1 模块总览

```
app/
├── modules/                         # ← 所有业务模块（分子模块化）
│   ├── core/                      # 核心模块
│   │   ├── auth/                 # 认证子模块
│   │   ├── admin/                # 系统管理子模块
│   │   └── workspace/            # 工作台/仪表盘子模块
│   │
│   ├── profile/                   # 个人中心模块
│   │   ├── routes.py
│   │   ├── service.py
│   │   ├── forms.py
│   │   └── templates/
│   │
│   ├── export/                   # 数据导出模块
│   │   ├── routes.py
│   │   ├── service.py
│   │   └── templates/
│   │
│   ├── fields/                   # ← 字段类型子模块（28个字段）
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── string.py
│   │   ├── string_long.py
│   │   └── ... (共28个)
│   │
│   └── taxonomy/                  # ← 词汇表子模块
│       ├── models.py
│       ├── service.py
│       └── templates/
│
├── routes/                        # 路由注册入口
│   └── __init__.py
│
├── services/                      # 公共服务
│   └── ...
│
├── models.py                      # 数据模型
└── forms/                        # 公共表单
```

### 2.2 模块说明

| 模块 | 路径 | 说明 |
|------|------|------|
| core/auth | modules/core/auth | 登录、登出、密码重置 |
| core/admin | modules/core/admin | 用户管理、系统设置、权限管理 |
| core/workspace | modules/core/workspace | 仪表盘、工作台 |
| profile | modules/profile | 个人资料、偏好设置、修改密码 |
| export | modules/export | 数据导出 |
| fields | modules/fields/ | 28 个字段类型模块 |
| taxonomy | modules/taxonomy | 词汇表管理 |

### 2.3 迁移计划

| 步骤 | 操作 | 源 | 目标 |
|------|------|-----|------|
| 1 | 创建模块目录 | - | app/modules/core/{auth,admin,workspace}/ |
| 2 | 迁移 auth | routes/auth.py | modules/core/auth/routes.py |
| 3 | 迁移 admin | routes/admin.py | modules/core/admin/routes.py |
| 4 | 拆分 workspace | main.py (dashboard) | modules/core/workspace/ |
| 5 | 拆分 profile | main.py (profile/settings) | modules/profile/ |
| 6 | 迁移 export | routes/export.py | modules/export/ |
| 7 | 创建 fields | - | modules/fields/ (28个) |
| 8 | 创建 taxonomy | - | modules/taxonomy/ |

---

## 四、URL 结构

### 4.1 节点类型管理（附加功能）

```
/nodes/types              # 节点类型列表
/nodes/types/new          # 创建节点类型
/nodes/types/<id>/edit   # 编辑节点类型
/nodes/types/<id>/delete # 删除节点类型
```

### 4.2 词汇表管理（附加功能）

```
/nodes/taxonomies             # 词汇表列表
/nodes/taxonomies/new         # 创建词汇表
/nodes/taxonomies/<id>/edit  # 编辑词汇表
/nodes/taxonomies/<id>/delete # 删除词汇表
```
app/
├── models.py                      # 数据模型（含 Node 相关）
├── services/
│   ├── node_service.py           # Node 服务层
│   └── taxonomy_service.py       # Taxonomy 服务层
├── forms/
│   └── node_forms.py             # 表单定义
├── routes/
│   └── node.py                   # 路由 Blueprint
├── modules/                      # ← 模块总目录
│   └── fields/                   # ← 字段类型模块
│       ├── __init__.py          # 模块注册器
│       ├── base.py              # 基类 BaseField
│       ├── text.py              # 单行文本
│       ├── textarea.py          # 多行文本
│       ├── number.py            # 整数
│       ├── decimal.py           # 小数
│       ├── date.py              # 日期
│       ├── datetime.py          # 日期时间
│       ├── select.py            # 下拉选择
│       ├── multi_select.py      # 多选
│       ├── checkbox.py          # 复选框
│       ├── radio.py             # 单选按钮
│       ├── email.py             # 邮箱
│       ├── phone.py             # 电话
│       ├── url.py               # 网址
│       ├── file.py              # 文件上传
│       ├── image.py             # 图片上传
│       └── relation.py          # 关联节点
│   └── workflows/               # ← 未来扩展：工作流模块
└── templates/
    └── node/                     # 模板目录
```

**说明：**
- `modules/`模块的总目录
 - 所有可复用- `modules/fields/` - 字段类型模块（当前实现）
 - `modules/workflows/` - 未来扩展：工作流模块

---

## 五、数据模型

### 3.1 FieldType（字段类型）

预定义的字段类型，不可修改。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 字段类型名称（如 text, number, date） |
| label | String | 显示标签（如 文本、数字、日期） |
| widget | String | 前端组件（input, textarea, select, checkbox） |
| field_settings | JSON | 字段配置（长度、必填等） |

### 3.2 NodeType（节点类型）

定义节点的字段结构。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 节点类型名称（如 客户信息） |
| slug | String | URL 标识（如 customer） |
| description | String | 描述 |
| fields_config | JSON | 字段配置数组 |
| is_active | Boolean | 是否启用 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

**fields_config 结构示例：**

```json
[
  {
    "field_type": "text",
    "name": "customer_name",
    "label": "客户名称",
    "required": true,
    "unique": false
  },
  {
    "field_type": "text",
    "name": "contact_person",
    "label": "联系人",
    "required": false,
    "unique": false
  }
]
```

### 3.3 Node（节点数据）

存储节点的实际数据。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| node_type_id | Integer | 关联 NodeType |
| data | JSON | 字段值（动态结构） |
| created_by | Integer | 创建人（关联 User） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

**data 结构示例：**

```json
{
  "customer_name": "ABC公司",
  "contact_person": "张三",
  "phone": "13800138000",
  "email": "zhangsan@example.com"
}
```

### 3.4 Taxonomy（词汇表）

存储选项列表。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 词汇表名称（如 客户类型） |
| slug | String | URL 标识（如 customer_type） |
| description | String | 描述 |
| items | JSON | 词汇项数组 |
| created_at | DateTime | 创建时间 |

**items 结构示例：**

```json
[
  {"id": 1, "name": "潜在客户"},
  {"id": 2, "name": "正式客户"},
  {"id": 3, "name": "VIP客户"}
]
```

### 3.5 TaxonomyReference（词汇表关联）

将词汇表关联到节点类型的字段。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| node_type_id | Integer | 关联 NodeType |
| field_name | String | 字段名称 |
| taxonomy_id | Integer | 关联 Taxonomy |

---

## 五、权限设计

### 4.1 权限键定义

| 权限键 | 说明 | 归属 |
|--------|------|------|
| `node.types.manage` | 管理节点类型 | 权限管理 |
| `node.taxonomy.manage` | 管理词汇表 | 权限管理 |
| `node.<type_slug>.create` | 创建某类型节点 | 节点类型 |
| `node.<type_slug>.read` | 读取某类型节点 | 节点类型 |
| `node.<type_slug>.update` | 更新某类型节点 | 节点类型 |
| `node.<type_slug>.delete` | 删除某类型节点 | 节点类型 |

### 4.2 权限管理方式

通过现有的权限系统（`permission_service.py` + 系统设置页面）进行管理。

---

## 六、实施步骤

### Step 1: 创建数据模型

**文件**: `app/models.py`

新增 5 个模型类：
- `FieldType` - 预定义字段类型
- `NodeType` - 节点类型定义
- `Node` - 节点数据
- `Taxonomy` - 词汇表
- `TaxonomyReference` - 词汇表关联

### Step 2: 创建服务层

**文件**: `app/services/node_service.py`

- `FieldTypeService` - 字段类型管理
- `NodeTypeService` - 节点类型 CRUD
- `NodeService` - 节点数据 CRUD
- `TaxonomyService` - 词汇表 CRUD

### Step 3: 创建表单

**文件**: `app/forms/node_forms.py`

- `NodeTypeForm` - 节点类型表单
- `NodeForm` - 节点数据表单（动态生成）
- `TaxonomyForm` - 词汇表表单

### Step 4: 创建路由 Blueprint

**文件**: `app/routes/node.py`

```python
node_bp = Blueprint('node', __name__, url_prefix='/nodes')
```

路由清单：
- `/nodes/types` - 节点类型列表
- `/nodes/types/new` - 创建节点类型
- `/nodes/types/<id>/edit` - 编辑节点类型
- `/nodes/types/<id>/delete` - 删除节点类型
- `/nodes/taxonomies` - 词汇表列表
- `/nodes/taxonomies/new` - 创建词汇表
- `/nodes/taxonomies/<id>/edit` - 编辑词汇表
- `/nodes/taxonomies/<id>/delete` - 删除词汇表
- `/nodes/<type_slug>` - 节点列表
- `/nodes/<type_slug>/new` - 创建节点
- `/nodes/<type_slug>/<id>` - 查看节点
- `/nodes/<type_slug>/<id>/edit` - 编辑节点
- `/nodes/<type_slug>/<id>/delete` - 删除节点

### Step 5: 创建模板

**目录**: `app/templates/node/`

| 文件 | 说明 |
|------|------|
| `types.html` | 节点类型列表 |
| `type_edit.html` | 节点类型编辑 |
| `taxonomies.html` | 词汇表列表 |
| `taxonomy_edit.html` | 词汇表编辑 |
| `nodes.html` | 节点列表 |
| `node_edit.html` | 节点编辑 |
| `node_view.html` | 节点查看 |

### Step 6: 注册 Blueprint

**文件**: `app/routes/__init__.py`

```python
from .node import node_bp
# ...
app.register_blueprint(node_bp)
```

### Step 7: 添加菜单入口

**文件**: `app/templates/frame_admin.html`

暂时在左侧菜单添加入口，后续会移出到独立菜单。

### Step 8: 创建示例"客户信息"

通过管理界面创建第一个节点类型：
- **名称**：客户信息
- **Slug**：customer
- **字段**：
  - 客户名称（文本，必填）
  - 联系人（文本）
  - 电话（文本）
  - 邮箱（文本）
  - 地址（文本）
  - 备注（多行文本）
- **词汇表**：客户类型（潜在客户、正式客户、VIP客户）

---

## 七、字段类型模块设计

### 7.1 模块文件命名（共 28 个）

| 序号 | Excel 字段类型 | 机器名 | 模块文件 | 内部属性 | 状态 |
|------|---------------|--------|----------|----------|------|
| 1 | Text (plain) | string | string.py | value | ✅ |
| 2 | Text (plain, long) | string_long | string_long.py | value | ✅ |
| 3 | Text (formatted) | text | text.py | value, format | ✅ |
| 4 | Text (formatted, long) | text_long | text_long.py | value, format | ✅ |
| 5 | Text (with summary) | text_with_summary | text_with_summary.py | value, summary, format | ✅ |
| 6 | Boolean | boolean | boolean.py | value | ✅ |
| 7 | Integer | integer | integer.py | value | ✅ |
| 8 | Decimal | decimal | decimal.py | value | ✅ |
| 9 | Float | float | float.py | value | ✅ |
| 10 | Content reference | entity_reference | entity_reference.py | target_id | ✅ |
| 11 | Taxonomy term | entity_reference | (同上) | target_id | ✅ |
| 12 | User reference | entity_reference | (同上) | target_id | ✅ |
| 13 | File | file | file.py | target_id, display, description | ✅ |
| 14 | Image | image | image.py | target_id, alt, title, width, height | ✅ |
| 15 | Link | link | link.py | uri, title, options | ✅ |
| 16 | Email | email | email.py | value | ✅ |
| 17 | Telephone | telephone | telephone.py | value | ✅ |
| 18 | Date | datetime | datetime.py | value | ✅ |
| 19 | Timestamp | timestamp | timestamp.py | value | ✅ |
| 20 | 多媒体库 (Media) | entity_reference | (entity_reference) | target_id | ✅ |
| 21 | 地理位置 (Geolocation) | geolocation | geolocation.py | lat, lng, address | ⏸️ |
| 22 | 颜色选择器 (Color) | color | color.py | color_code, opacity | ✅ |
| 23 | 智能标签 (AI Tags) | ai_tags | ai_tags.py | term_id, confidence_score | ⏸️ |
| 24 | 证件识别码 | identity | identity.py | id_number, id_type, is_verified | ✅ |
| 25 | 隐私脱敏字段 | masked | masked.py | raw_value, display_value, permission_level | ✅ |
| 26 | 生物特征引用 | biometric | biometric.py | feature_vector, type, version | ✅ |
| 27 | 标准地址字段 (Address) | address | address.py | province, city, district, street, house_number, grid_id | ✅ |
| 28 | 地理围栏 (GIS) | gis | gis.py | point, spatial_ref | ⏸️ |

**说明**：
- ✅ = 完整实现
- ⏸️ = 延后（仅建立基本结构）

### 7.2 内部属性设计

所有字段的内部属性（properties）用 JSON 存储，示例：

```python
# string 字段
{"value": "客户名称"}

# entity_reference 字段
{"target_id": 5, "target_type": "node"}

# address 字段
{"province": "广东省", "city": "深圳市", "district": "南山区", "street": "科技园路", "house_number": "100号", "grid_id": "440305001"}

# image 字段
{"target_id": 10, "alt": "产品图片", "title": "产品展示图", "width": 800, "height": 600}
```

### 7.3 BaseField 接口设计

```python
class BaseField:
    """字段类型基类"""
    name = None           # 机器名，如 string, integer
    label = None         # 显示标签，如 "单行文本"
    widget = None         # 前端组件，如 input, select
    properties = []       # 内部属性列表
    
    def __init__(self, field_name, field_config):
        self.field_name = field_name
        self.field_config = field_config  # JSON 配置
    
    def render(self, value, mode='edit'):
        """渲染 HTML
        - value: 当前值（dict）
        - mode: edit/view
        """
        raise NotImplementedError
    
    def validate(self, value):
        """验证数据，返回错误列表"""
        return []
    
    def format(self, value):
        """格式化显示"""
        return value
    
    def get_widget_config(self):
        """获取前端组件配置"""
        return {}
```

### 7.4 延后字段的基本结构

对于延后的 3 个字段（geolocation, ai_tags, gis），仅建立字段结构：

```python
# geolocation.py - 地理位置
class GeolocationField(BaseField):
    name = 'geolocation'
    label = '地理位置'
    widget = 'geolocation_input'
    properties = ['lat', 'lng', 'address']
    # 基本结构已建立，等待引入地图库后实现完整功能

# ai_tags.py - 智能标签
class AITagsField(BaseField):
    name = 'ai_tags'
    label = '智能标签'
    widget = 'ai_tags_input'
    properties = ['term_id', 'confidence_score']
    # 基本结构已建立，等待 AI 服务接入后实现

# gis.py - 地理围栏
class GISField(BaseField):
    name = 'gis'
    label = '地理围栏'
    widget = 'gis_input'
    properties = ['point', 'spatial_ref']
    # 基本结构已建立，等待地图功能完善后实现
```

### 7.5 第三方库（仅已实现字段）

| 字段类型 | 第三方库 | 用途 |
|----------|----------|------|
| image / file | Dropzone.js | 文件上传组件 |
| color | vue-color-kit | 颜色选择器 |
| geolocation / gis | (延后) | 地图选择器 |
| ai_tags | (延后) | AI 服务 |

### 7.6 目录结构

```
app/modules/fields/
├── __init__.py              # 模块注册器
├── base.py                  # 基类 BaseField
├── string.py               # 单行文本
├── string_long.py          # 多行纯文本
├── text.py                 # 带格式文本
├── text_long.py            # 带格式长文本
├── text_with_summary.py    # 含摘要文本
├── boolean.py              # 布尔值
├── integer.py              # 整数
├── decimal.py              # 精确小数
├── float.py                # 浮点数
├── entity_reference.py     # 关联引用
├── file.py                 # 文件
├── image.py                # 图片
├── link.py                 # 链接
├── email.py                # 邮箱
├── telephone.py            # 电话
├── datetime.py             # 日期时间
├── timestamp.py            # 时间戳
├── geolocation.py           # 地理位置 ⏸️
├── color.py                 # 颜色选择器
├── ai_tags.py              # 智能标签 ⏸️
├── identity.py             # 证件识别码
├── masked.py               # 隐私脱敏字段
├── biometric.py            # 生物特征引用
├── address.py              # 标准地址字段
└── gis.py                  # 地理围栏 ⏸️
```

---

## 八、后续扩展

1. **数据分析功能**
   - 统计图表
   - 数据可视化

2. **导出/导入功能**
   - CSV 导出
   - Excel 导出
   - 数据导入

3. **菜单重构**
   - 将 Node 相关菜单从 frame admin 移出
   - 创建独立的导航菜单

---

## 九、文件清单

### 字段类型模块（modules/fields/）

| 序号 | 文件 | 操作 |
|------|------|------|
| 1 | `app/modules/fields/__init__.py` | 新建 - 模块注册器 |
| 2 | `app/modules/fields/base.py` | 新建 - 基类 BaseField |
| 3 | `app/modules/fields/text.py` | 新建 - 单行文本 |
| 4 | `app/modules/fields/textarea.py` | 新建 - 多行文本 |
| 5 | `app/modules/fields/number.py` | 新建 - 整数 |
| 6 | `app/modules/fields/decimal.py` | 新建 - 小数 |
| 7 | `app/modules/fields/date.py` | 新建 - 日期 |
| 8 | `app/modules/fields/datetime.py` | 新建 - 日期时间 |
| 9 | `app/modules/fields/select.py` | 新建 - 下拉选择 |
| 10 | `app/modules/fields/multi_select.py` | 新建 - 多选 |
| 11 | `app/modules/fields/checkbox.py` | 新建 - 复选框 |
| 12 | `app/modules/fields/radio.py` | 新建 - 单选按钮 |
| 13 | `app/modules/fields/email.py` | 新建 - 邮箱 |
| 14 | `app/modules/fields/phone.py` | 新建 - 电话 |
| 15 | `app/modules/fields/url.py` | 新建 - 网址 |
| 16 | `app/modules/fields/file.py` | 新建 - 文件上传 |
| 17 | `app/modules/fields/image.py` | 新建 - 图片上传 |
| 18 | `app/modules/fields/relation.py` | 新建 - 关联节点 |

### 其他文件

| 序号 | 文件 | 操作 |
|------|------|------|
| 19 | `app/models.py` | 修改 - 添加 5 个模型 |
| 20 | `app/services/node_service.py` | 新建 - 服务层 |
| 21 | `app/forms/node_forms.py` | 新建 - 表单 |
| 22 | `app/routes/node.py` | 新建 - 路由 |
| 23 | `app/routes/__init__.py` | 修改 - 注册 Blueprint |
| 24 | `app/templates/node/types.html` | 新建 - 模板 |
| 25 | `app/templates/node/type_edit.html` | 新建 - 模板 |
| 26 | `app/templates/node/taxonomies.html` | 新建 - 模板 |
| 27 | `app/templates/node/taxonomy_edit.html` | 新建 - 模板 |
| 28 | `app/templates/node/nodes.html` | 新建 - 模板 |
| 29 | `app/templates/node/node_edit.html` | 新建 - 模板 |
| 30 | `app/templates/node/node_view.html` | 新建 - 模板 |
| 31 | `app/templates/frame_admin.html` | 修改 - 添加菜单 |

---

## 十、示例数据

### 9.1 字段类型（预置）

| name | label | widget |
|------|-------|--------|
| text | 单行文本 | input |
| textarea | 多行文本 | textarea |
| number | 数字 | input |
| decimal | 小数 | input |
| date | 日期 | input(type=date) |
| datetime | 日期时间 | input(type=datetime-local) |
| select | 下拉选择 | select |
| multi_select | 多选 | select(multiple) |
| checkbox | 复选框 | input(type=checkbox) |
| radio | 单选按钮 | input(type=radio) |
| email | 邮箱 | input(type=email) |
| phone | 电话 | input(type=tel) |
| url | 网址 | input(type=url) |
| file | 文件上传 | input(type=file) |
| image | 图片上传 | input(type=file) |
| relation | 关联节点 | select(dynamic) |

### 9.2 示例：客户信息节点类型

**节点类型**：
- 名称：客户信息
- Slug：customer
- 描述：记录客户基本信息

**字段配置**：

| 字段名 | 字段类型 | 标签 | 必填 | 唯一 |
|--------|----------|------|------|------|
| customer_name | text | 客户名称 | 是 | 是 |
| contact_person | text | 联系人 | 否 | 否 |
| phone | phone | 电话 | 否 | 否 |
| email | email | 邮箱 | 否 | 否 |
| address | textarea | 地址 | 否 | 否 |
| customer_type | relation | 客户类型 | 否 | 否 |
| notes | textarea | 备注 | 否 | 否 |

**词汇表 - 客户类型**：
- 潜在客户
- 正式客户
- VIP客户

---

## 十一、Taxonomy 模块设计

### 11.1 子模块结构

```
app/modules/
├── fields/           # 字段类型模块
│   ├── __init__.py
│   ├── base.py
│   └── ...          # 28 个字段类型文件
│
└── taxonomy/         # ← Taxonomy 子模块
    ├── __init__.py
    ├── models.py    # Taxonomy, TaxonomyItem 模型
    └── service.py   # TaxonomyService
```

### 11.2 数据模型

#### Taxonomy (词汇表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 词汇表名称 |
| slug | String | URL 标识 |
| description | String | 描述 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

#### TaxonomyItem (词汇项)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| taxonomy_id | Integer | 关联 Taxonomy |
| name | String | 词汇名称 |
| description | String | 描述（可选） |
| weight | Integer | 排序权重 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 11.3 前端结构

#### 词汇表列表页（折叠面板）

```
词汇表列表
├── 词汇表 A（点击展开）
│   ├── 词汇项表格
│   │   ├── 词汇1 [编辑] [删除]
│   │   ├── 词汇2 [编辑] [删除]
│   │   └── [+ 新增词汇]
│   └── [预留 AI 批量添加按钮]
├── 词汇表 B（点击展开）
│   └── ...
└── [+ 新增词汇表]
```

#### 新页面

| 页面 | URL | 说明 |
|------|-----|------|
| 新增词汇表 | `/nodes/taxonomies/new` | 创建新词汇表 |
| 编辑词汇表 | `/nodes/taxonomies/<id>/edit` | 编辑词汇表 |
| 查看词汇表 | `/nodes/taxonomies/<id>` | 查看词汇表及词汇项 |

### 11.4 后端接口

| 方法 | URL | 说明 |
|------|-----|------|
| GET | `/nodes/taxonomies` | 词汇表列表 |
| POST | `/nodes/taxonomies` | 创建词汇表 |
| GET | `/nodes/taxonomies/<id>` | 查看词汇表及词汇项 |
| PUT | `/nodes/taxonomies/<id>` | 更新词汇表 |
| DELETE | `/nodes/taxonomies/<id>` | 删除词汇表 |
| POST | `/nodes/taxonomies/<id>/items` | 新增词汇项 |
| PUT | `/nodes/taxonomies/<id>/items/<item_id>` | 更新词汇项 |
| DELETE | `/nodes/taxonomies/<id>/items/<item_id>` | 删除词汇项 |
| POST | `/nodes/taxonomies/<id>/ai-generate` | AI 生成词汇项（预留接口）|

### 11.5 AI 功能预留

```python
# service.py 中预留接口
class TaxonomyService:
    @staticmethod
    def generate_items_ai(taxonomy_id, count=10):
        """AI 生成词汇项（预留接口）
        
        用户可通过 OpenCode 直接调用此接口生成词汇项
        """
        # TODO: 实现 AI 生成逻辑
        pass
```

---

## 十二、版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-03-12 | 初始版本 |
| 1.1 | 2026-03-12 | 增加字段类型模块化设计（modules/fields/） |
| 1.2 | 2026-03-12 | 增加 Taxonomy 子模块设计（modules/taxonomy/） |
