# core/models 模型设计规范

> 文档版本：2.0  
> 创建日期：2026-04-07  
> 最后更新：2026-07-22

---

## 一、概述

### 1.1 模块定位

`core/models.py` 及相关子模块模型是整个系统的核心数据层，定义了用户、权限、系统配置、内容分类等基础实体。

### 1.2 BaseModel 抽象基类

项目提供 `BaseModel` 抽象基类（`core/models.py:32-38`），所有模型应继承此类以获得公共字段：

```python
class BaseModel(models.Model):
    """抽象基础模型，提供公共时间戳字段"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        abstract = True
```

**使用方式**：
```python
class MyModel(BaseModel):
    name = models.CharField(max_length=100)
```

### 1.3 全局常量引用

模型中使用的枚举值统一从 `core/constants.py` 引用：

| 常量类 | 来源 | 用途 |
|--------|------|------|
| `UserRole` | `core.constants.UserRole` | 用户角色（MANAGER/LEADER/EMPLOYEE） |
| `UserTheme` | `core.constants.UserTheme` | 用户主题（DEFAULT/GOV/INDIGO 等） |
| `ModuleType` | `core.constants.ModuleType` | 模块类型（NODE/SYSTEM/TOOL） |
| `Language` | `core.constants.Language` | 界面语言（ZH/EN） |

**模型中使用示例**：
```python
from core.constants import UserRole, UserTheme

class User(AbstractUser):
    class Role(models.TextChoices):
        MANAGER = UserRole.MANAGER, UserRole.LABELS[UserRole.MANAGER]
        LEADER = UserRole.LEADER, UserRole.LABELS[UserRole.LEADER]
        EMPLOYEE = UserRole.EMPLOYEE, UserRole.LABELS[UserRole.EMPLOYEE]
    
    class Theme(models.TextChoices):
        DEFAULT = UserTheme.DEFAULT, UserTheme.LABELS[UserTheme.DEFAULT]
        # ...
```

### 1.4 模型分布

| 文件 | 模型 | 用途 |
|------|------|------|
| `core/models.py` | User, SystemSetting, Taxonomy, TaxonomyItem, ChinaRegion, IsActiveMixin（抽象混入类） | 核心基础数据（5个具体模型 + 2个抽象类） |
| `core/node/models.py` | NodeType, Node | 节点系统模型 |
| `core/module/models.py` | Module, ToolType | 模块注册与工具类型 |
| `core/smtp/models.py` | EmailTemplate, EmailLog | 邮件系统模型 |

**模型总计**：12 个具体模型 + 2 个抽象基类（BaseModel, IsActiveMixin）

> **注意**：User 模型继承自 `AbstractUser`（Django 内置），而非 `BaseModel`。

---

## 二、User 模型

### 2.1 用途
用户认证、权限控制、个人偏好存储

### 2.2 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `username` | CharField | 用户名（AbstractUser 继承） |
| `nickname` | CharField | 昵称（优先显示于仪表盘等处） |
| `email` | EmailField | 邮箱（可选，用于密码重置、通知） |
| `is_active` | BooleanField | 激活状态（`db_index=True, default=True`，重写 AbstractUser） |
| `is_admin` | BooleanField | 是否为系统管理员 |
| `role` | CharField | 角色：manager/leader/employee |
| `permissions` | JSONField | 细粒度权限列表 |
| `theme` | CharField | 界面主题 |
| `preferred_language` | CharField | 首选语言：zh/en |
| `navigation_cards` | JSONField | 导航卡片配置 |
| `notifications_enabled` | BooleanField | 是否启用系统通知 |
| `failed_login_attempts` | IntegerField | 登录失败次数 |
| `locked_until` | DateTimeField | 账号锁定截止时间 |
| `last_login_at` | DateTimeField | 最后登录时间 |
| `created_at` | DateTimeField | 创建时间 |
| `updated_at` | DateTimeField | 更新时间 |

### 2.3 内部类

| 类 | 说明 |
|------|------|
| `Role` | 角色枚举，值引用 `core.constants.UserRole` |
| `Theme` | 主题枚举，值引用 `core.constants.UserTheme` |
| `UserManager` | 自定义用户管理器 |

### 2.4 方法

| 方法 | 说明 |
|------|------|
| `is_locked()` | 判断账号是否处于锁定状态 |
| `record_login()` | 记录成功登录时间 |
| `record_failed_attempt()` | 记录登录失败，达到阈值后锁定账号 |
| `reset_failed_attempts()` | 登录成功或手动重置时，清零失败计数 |

---

## 三、SystemSetting 模型

### 3.1 用途
系统配置键值对存储，通过 SettingsService 统一读写

### 3.2 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `key` | CharField | 配置键（唯一） |
| `value` | TextField | 配置值（统一存字符串，服务层负责类型转换） |
| `description` | CharField | 配置描述 |
| `updated_at` | DateTimeField | 更新时间 |

---

## 四、Taxonomy 模型

### 4.1 用途
词汇表，用于分类和组织内容的层级结构

### 4.2 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | CharField | 词汇表名称 |
| `slug` | CharField | URL 标识（唯一） |
| `description` | CharField | 描述 |
| `created_at` | DateTimeField | 创建时间 |
| `updated_at` | DateTimeField | 更新时间 |

### 4.3 关联模型：TaxonomyItem

| 字段 | 类型 | 说明 |
|------|------|------|
| `taxonomy` | ForeignKey | 所属词汇表 |
| `name` | CharField | 词汇名称 |
| `description` | CharField | 描述 |
| `weight` | IntegerField | 排序权重 |
| `created_at` | DateTimeField | 创建时间 |
| `updated_at` | DateTimeField | 更新时间 |

**约束**：`unique_together = [["taxonomy", "name"]]`

---

## 五、ChinaRegion 模型

### 5.1 用途
中国行政区划，省市县三级联动

### 5.2 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | CharField | 行政区划代码（6位，`unique=True`） |
| `name` | CharField | 名称 |
| `level` | IntegerField | 层级：1=省级、2=地级市、3=县/区（`choices=LEVEL_CHOICES, db_index=True`） |
| `parent` | ForeignKey | 父级行政区划（自关联，`on_delete=PROTECT`） |
| `created_at` | DateTimeField | 创建时间 |

### 5.3 方法

| 方法 | 说明 |
|------|------|
| `full_path` (property) | 获取完整路径，如"广东省 - 深圳市 - 南山区" |

---

## 六、NodeType 模型

### 6.1 用途
定义节点的结构，包括名称、标识符、字段配置等

### 6.2 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | CharField | 节点类型名称 |
| `slug` | CharField | 标识符（唯一） |
| `description` | CharField | 描述 |
| `icon` | CharField | 图标（Bootstrap Icons） |
| `author` | CharField | 作者 |
| `fields_config` | JSONField | 字段配置 |
| `is_active` | BooleanField | 是否启用 |
| `created_at` | DateTimeField | 创建时间 |
| `updated_at` | DateTimeField | 更新时间 |

### 6.3 方法

| 方法 | 说明 |
|------|------|
| `get_node_count()` | 获取该类型的节点数量 |

---

## 七、Node 模型

### 7.1 用途
节点主表，所有节点类型的公共字段

### 7.2 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `node_type` | ForeignKey | 节点类型 |
| `created_by` | ForeignKey | 创建人（`on_delete=SET_NULL, null=True, blank=True`） |
| `updated_by` | ForeignKey | 更新人（`on_delete=SET_NULL, null=True, blank=True`） |
| `created_at` | DateTimeField | 创建时间 |
| `updated_at` | DateTimeField | 更新时间 |

---

## 八、Module 模型

### 8.1 用途
模块注册表，记录已安装的模块信息

### 8.2 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `module_id` | CharField | 模块ID（唯一） |
| `name` | CharField | 模块名称 |
| `version` | CharField | 版本号 |
| `author` | CharField | 作者 |
| `description` | TextField | 描述 |
| `icon` | CharField | 图标类名 |
| `path` | CharField | 模块路径 |
| `is_installed` | BooleanField | 是否已安装 |
| `is_active` | BooleanField | 是否启用 |
| `is_system` | BooleanField | 是否系统默认模块 |
| `module_type` | CharField | 模块类型：node/system/tool（使用 ModuleType 常量） |
| `install_on_init` | BooleanField | 是否在初始化时自动安装 |
| `installed_at` | DateTimeField | 安装时间 |
| `activated_at` | DateTimeField | 启用时间 |
| `created_at` | DateTimeField | 创建时间 |
| `updated_at` | DateTimeField | 更新时间 |

### 8.3 方法

| 方法 | 说明 |
|------|------|
| `path_exists` (property) | 检查模块目录是否存在 |
| `get_active_ids(module_type=None)` (classmethod) | 获取启用模块 ID 列表，可选按 `module_type` 过滤；返回 `list[str]` |

---

## 九、ToolType 模型

### 9.1 用途
工具类型注册表，用于协作工具（tool）类型模块的分类

### 9.2 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | CharField | 工具名称 |
| `slug` | CharField | 标识符（唯一） |
| `description` | CharField | 描述 |
| `icon` | CharField | 图标（Bootstrap Icons） |
| `author` | CharField | 作者 |
| `is_active` | BooleanField | 是否启用 |
| `created_at` | DateTimeField | 创建时间 |
| `updated_at` | DateTimeField | 更新时间 |

---

## 十、EmailTemplate 模型

### 10.1 用途
邮件模板管理

### 10.2 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | CharField | 模板标识（唯一） |
| `subject` | CharField | 邮件主题模板 |
| `html_body` | TextField | HTML 正文模板 |
| `text_body` | TextField | 纯文本正文模板 |
| `description` | CharField | 模板说明 |
| `is_active` | BooleanField | 是否启用 |
| `created_at` | DateTimeField | 创建时间 |
| `updated_at` | DateTimeField | 更新时间 |

---

## 十一、EmailLog 模型

### 11.1 用途
邮件发送记录追踪

### 11.2 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `from_email` | EmailField | 发件人 |
| `to_email` | TextField | 收件人（允许多个收件人） |
| `subject` | CharField | 邮件主题 |
| `text_body` | TextField | 纯文本正文 |
| `html_body` | TextField | HTML 正文 |
| `template_name` | CharField | 使用的模板 |
| `status` | CharField | 状态：pending/sending/sent/failed（`db_index=True`） |
| `error_message` | TextField | 错误信息 |
| `retry_count` | IntegerField | 重试次数 |
| `created_at` | DateTimeField | 创建时间 |
| `sent_at` | DateTimeField | 发送时间 |

---

## 十二、模型关系图

```
User (1) ←──→ (N) Node
                    ↑
                    │
               NodeType (1) ←──→ (N) Node

Module (1) ────→ NodeType (通过 module_id ↔ slug 关联)
  │
  ├── module_type='node'  → 创建/关联 NodeType
  ├── module_type='tool'  → 创建/关联 ToolType
  └── module_type='system'→ 不创建类型

ToolType (1) ←──→ (N) tool 类型模块

Taxonomy (1) ←──→ (N) TaxonomyItem

ChinaRegion (1) ←─→ (N) ChinaRegion (parent)

EmailTemplate (独立)

EmailLog (独立)
```

---

## 十三、约束与规范

### 12.1 命名规范
- 模型类名：PascalCase（首字母大写），如 `User`, `SystemSetting`
- 表名：`db_table` 指定小写加下划线，如 `users`, `system_settings`
- 字段名：小写加下划线，如 `created_at`, `is_active`

### 12.2 必填字段
- 所有模型必须有 `created_at` 和 `updated_at` 字段
- 关键实体应有 `verbose_name` 和 `help_text`

### 12.3 外键约束
- 删除时使用 `CASCADE`，除非业务需要保留数据
- 外键字段应设置 `related_name` 便于反向查询

### 12.4 JSONField 使用场景
- `permissions`: 细粒度权限列表
- `fields_config`: 节点字段配置
- `navigation_cards`: 导航卡片配置
- 存储结构化数据且不需要数据库查询时使用

---

---

