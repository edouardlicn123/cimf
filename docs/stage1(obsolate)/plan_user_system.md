# 用户系统改进计划

**最后更新**: 2026-03-10

---

##1. 将用户 需求概述

分为三类：**管理员**、**组长**、**普通员工**
2. 组长和普通员工的权限可编辑，增加专用权限编辑页面
3. 新增人员管理页（列表页 + 新建/编辑页）
4. admin 账号（id=1）权限不可编辑，且在人员管理页隐藏

---

## 方案设计

### 1. 数据模型扩展

在 `User` 模型中添加两个字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `role` | String(20) | 角色：admin/leader/employee |
| `permissions` | JSON | 细粒度权限覆盖 |

```python
# app/models.py
role = db.Column(
    db.String(20),
    default='employee',
    nullable=False,
    comment="角色：admin/leader/employee"
)

permissions = db.Column(
    db.JSON,
    default=dict,
    comment="细粒度权限（JSON）"
)
```

### 2. 权限服务层

新建 `app/services/permission_service.py`：

```python
# 权限列表（保留扩展性）
PERMISSIONS = [
    ('system.manage', '系统管理 - 访问后台'),
    ('system.settings', '系统设置 - 修改配置'),
    ('user.manage', '用户管理 - 增删改查'),
    # 未来可扩展：
    # ('project.view', '项目 - 查看'),
    # ('report.export', '报表 - 导出'),
]

# 角色默认权限
ROLE_DEFAULT_PERMISSIONS = {
    'admin': ['*'],        # 全部权限
    'leader': ['system.manage', 'system.settings', 'user.manage'],
    'employee': []         # 普通员工无额外权限
}
```

### 3. admin 账号保护机制

| 保护项 | 实现 |
|--------|------|
| 全部权限 | `role='admin' → permissions=['*']` |
| 不可编辑 | `id=1` 的用户在列表隐藏、编辑页只读 |
| 强制设置 | 创建/更新用户时，id=1 强制 role='admin', permissions=['*'] |

---

## 实施步骤

### 阶段一：基础架构

| 步骤 | 内容 | 文件 |
|------|------|------|
| 1.1 | 扩展 User 模型，添加 role 和 permissions 字段 | `app/models.py` |
| 1.2 | 创建权限服务层 | `app/services/permission_service.py` |
| 1.3 | 修改用户服务，添加 admin 保护 | `app/services/user_service.py` |
| 1.4 | 修改用户表单，添加角色选择 | `app/forms/admin_forms.py` |

### 阶段二：权限编辑页面

| 步骤 | 内容 | 文件 |
|------|------|------|
| 2.1 | 新增权限编辑路由 | `app/routes/admin.py` |
| 2.2 | 创建权限编辑模板 | `app/templates/admin/permissions.html` |

### 阶段三：admin 保护

| 步骤 | 内容 | 文件 |
|------|------|------|
| 3.1 | 用户列表隐藏 admin | `app/services/user_service.py` |
| 3.2 | 编辑页 admin 只读 | `app/templates/admin/system_user_edit.html` |

---

## 权限矩阵设计

### UI 界面

```
┌─────────────────────────┬──────────┬──────────┬────────────┐
│ 权限名称                │ 管理员   │ 组长     │ 普通员工   │
├─────────────────────────┼──────────┼──────────┼────────────┤
│ 系统管理                │    ✓     │    ✓     │     ✗      │
│ 系统设置                │    ✓     │    ✓     │     ✗      │
│ 用户管理                │    ✓     │    ✓     │     ✗      │
│ (未来扩展...)           │   ...    │   ...    │    ...     │
└─────────────────────────┴──────────┴──────────┴────────────┘
```

### 角色说明

| 角色 | 标识 | 默认权限 | 说明 |
|------|------|---------|------|
| 管理员 | admin | ['*'] | 拥有全部权限，不可编辑 |
| 组长 | leader | 可配置 | 由管理员分配权限 |
| 普通员工 | employee | 可配置 | 由管理员分配权限 |

---

## 涉及修改的文件清单

| 文件路径 | 操作 | 说明 |
|---------|------|------|
| app/models.py | 修改 | 添加 role, permissions 字段 |
| app/services/permission_service.py | 新建 | 权限服务层 |
| app/services/user_service.py | 修改 | 添加 admin 保护逻辑 |
| app/forms/admin_forms.py | 修改 | 添加角色选择字段 |
| app/routes/admin.py | 修改 | 添加权限编辑路由 |
| app/templates/admin/permissions.html | 新建 | 权限矩阵页面 |
| app/templates/admin/system_user_edit.html | 修改 | admin 只读处理 |
| docs/PROGRESS.md | 更新 | 记录开发进度 |

---

## 变更记录

- 2026-03-10：创建用户系统改进计划
