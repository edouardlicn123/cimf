# AGENTS.md

## 开发规范

在每次会话开始时，请读取 `docs/开发规范.md` 以了解最新的开发规范。

## 重要约束

- **Node 字段类型**：开发 node 模块时，字段必须从现有的字段类型中选取。可通过 `/nodes/field-types` 查看完整列表。

## Node 类型开发规范

### 目录结构

每个 Node 类型必须有独立的子目录，遵循以下结构：

```
app/
├── models/node/                  # Node 专用模型
│   ├── node_type.py
│   └── node.py
├── services/node/                # Node 服务层
│   ├── node_type_service.py
│   ├── node_service.py
│   └── {node_slug}/             # 如 customer/
│       └── customer_service.py
├── modules/node/                 # Node 主模块
│   ├── routes.py
│   ├── forms.py
│   └── {node_slug}/              # 如 customer/
│       ├── routes.py
│       └── forms.py
└── templates/node/               # Node 模板
    ├── frame_node_type.html
    ├── node_type_list.html
    ├── node_type_edit.html
    ├── node_list.html
    ├── node_view.html
    ├── node_edit.html
    └── {node_slug}/              # 如 customer/
        ├── list.html
        ├── view.html
        └── edit.html
```

### 字段类型规范

- **必须**从系统预定义字段类型中选择（24 种）
- 系统字段类型位于 `app/modules/core/fields/`
- 如需创建自定义字段类型，参考 `app/modules/core/fields/base.py` 中的 `BaseField` 基类
- 自定义字段类型文件放在 `app/modules/fields/` 目录下

### 命名规范

- **节点类型机器名**：使用小写字母和下划线，如 `customer`、`project`、`order`
- **目录名**：与机器名一致，如 `customer/`
- **类名**：使用 PascalCase，如 `CustomerService`、`CustomerForm`

## Progress 文档规范

每次修改必须写入 progress 文档，格式要求：
- 文件路径：`docs/progress.md`
- 内容格式：日期-当日修改内容
- 每次写入前删除之前的内容，只保留当日的修改记录

示例：
```markdown
# 2026-03-13 修改记录

1. 修复了表单无法完全占满卡片的问题 - 修改了主题文件中的 .card-body 样式
2. 更新了权限管理页面的布局 - 与系统设置页保持一致
3. 修复了词汇表管理页底部内容不可见的问题 - 移除了 overflow: hidden
```

## Flash/Toast 消息规范

### 需要加入 Flash/Toast 的页面类型

| 页面类型 | 说明 | 示例 |
|----------|------|------|
| 错误页面 | 400, 401, 404, 500 错误页面 | errors/400.html |
| 认证页面 | 登录等认证相关页面 | auth/login.html |
| 仪表盘 | 工作区/个人仪表盘 | dashboard.html |
| 个人中心 | 个人资料、设置等页面 | profile.html, settings.html |
| 管理后台 | 所有系统管理页面 | system_users.html, system_settings.html |
| 内容结构 | 所有内容结构管理页面 | taxonomies.html, field_types.html |

### 不需要加入的页面类型

| 页面类型 | 说明 |
|----------|------|
| 基础模板 | base.html |
| 框架模板 | frame_admin.html, frame_structure.html |
| 包含模板 | includes/ 目录下的 header.html, nav.html, footer.html 等 |
| 组件模板 | toast_messages.html, flash_messages.html |

### 实现方式

在页面中引入 toast 组件，并确保 flash 信息被 CSS 隐藏（只显示 toast）：

```html
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 9999;">
      {% for category, message in messages %}
        <div class="toast show" role="alert">
          <div class="toast-body">
            {{ message }}
          </div>
        </div>
      {% endfor %}
    </div>
  {% endif %}
{% endwith %}
```

**重要：Flash 信息必须隐藏**

在页面样式中添加以下 CSS，确保传统的 flash 消息被隐藏，只显示 toast：

```css
/* 隐藏传统 flash 消息，只显示 toast */
.alert, .flash-message, .flashed-messages {
  display: none !important;
}
```

## 页面模板变量规范

### 要求

所有新创建的页面模板（即**内容模板**，非框架模板），**必须**在模板开头添加以下变量声明：

```html
{% set show_nav = true %}
{% set show_header = false %}
```

### 变量说明

| 变量 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| show_nav | bool | true | 是否显示顶部导航栏 |
| show_header | bool | true | 是否显示页面标题栏 |

**注意**：这些变量写在**内容模板**中（如 system_settings.html），不是框架模板（如base.html frame_admin.html）。框架模板通过 Jinja2 的 set 标签接收这些变量。


