# Models 层拆分计划

## 一、概述

将 `app/models.py` 拆分为 `app/models/` 目录，与 modules 层结构保持一致。

## 二、目标结构

```
app/
├── models/                  # ← 新建
│   ├── __init__.py         # 导出所有模型
│   ├── user.py             # User 模型
│   └── system_setting.py   # SystemSetting 模型
├── services/
├── forms/
└── modules/
```

## 三、实施步骤

### Step 1: 创建 models 目录

```bash
mkdir -p app/models
touch app/models/__init__.py
```

### Step 2: 创建 user.py

从 `app/models.py` 提取 User 类，保存为 `app/models/user.py`

### Step 3: 创建 system_setting.py

从 `app/models.py` 提取 SystemSetting 类，保存为 `app/models/system_setting.py`

### Step 4: 创建 __init__.py

```python
from .user import User
from .system_setting import SystemSetting

__all__ = ['User', 'SystemSetting']
```

### Step 5: 删除原 models.py

```bash
rm app/models.py
```

**无需修改任何现有导入**，因为 Python 会自动从 `app/models/__init__.py` 导入。

## 四、需要修改的文件

| 操作 | 文件 |
|------|------|
| 新建 | `app/models/__init__.py` |
| 新建 | `app/models/user.py` |
| 新建 | `app/models/system_setting.py` |
| **删除** | `app/models.py` |

## 五、导入说明

拆分后，所有现有导入仍然有效：

```python
# 以下导入方式都能正常工作
from app.models import User
from app.models import SystemSetting
from app.models.user import User
from app.models.system_setting import SystemSetting
```

原因：Python 会先找 `app/models.py`，找不到时自动找 `app/models/__init__.py`。

## 六、后续扩展

拆分后便于添加后续模型：

```
app/models/
├── __init__.py
├── user.py
├── system_setting.py
├── taxonomy.py         # Taxonomy, TaxonomyItem
└── node.py             # NodeType, Node, FieldType
```

## 七、版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-03-12 | 初始版本 |
| 1.1 | 2026-03-12 | 修正：删除原 models.py，无需保留兼容层 |
