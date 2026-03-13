以下是针对你最新补充需求的更新版本策划书。我在其中加入了“frame 的颜色主要继承 default（以及后台切换的主题）的用色”这一原则，并把之前提供的线框草图也补充进来。

**FFE 项目跟进系统 - 后台管理页面布局策划书（更新版）**

**文档版本**：1.1  
**更新日期**：2026年2月14日  
**项目代号**：FFE  
**主要变更**：  
- 明确 frame 配色继承原则  
- 补充左侧导航 + 右侧内容区的线框草图

### 1. 设计目标（不变）

- 提供统一的后台管理布局（左侧窄导航 + 右侧宽内容区）
- 风格参考 LinkedIn / 现代 SaaS 后台（简洁、专业、可扩展）
- 左侧导航的“当前选中/高亮”状态跟随右侧页面自动对应
- 最大程度复用现有主题系统与 class 命名规范
- 布局逻辑与高亮判断集中在 frame_admin.html

### 2. 模板继承链（不变）

```
base.html
   ↑
frame_admin.html
   ↑
admin/settings.html
admin/users.html
admin/user_edit.html
...
```

### 3. 主要模板文件说明（不变）

| 文件路径                        | 作用                               | 是否继承          | 主要 block / 变量                     |
|--------------------------------|------------------------------------|-------------------|---------------------------------------|
| templates/base.html            | 全站最外层                         | —                 | content、extra_head 等                |
| templates/frame_admin.html     | 后台通用左右分栏布局               | 继承 base.html    | admin_content、active_section         |
| templates/admin/xxx.html       | 具体功能页面                       | 继承 frame_admin.html | 仅填充 admin_content + set active_section |

### 4. 核心设计决策（更新）

4.1 左侧导航高亮逻辑（不变）  
每个子页面顶部声明：

```jinja
{% set active_section = 'settings' %}
{% set active_section = 'users' %}
```

frame_admin.html 中使用该变量判断 active 类。

4.2 样式文件命名与职责（不变）

- 全局主题：default.css / macaron.css / dopamine.css 等
- 后台专用微调：**static/css/frame.css**（轻量，只写布局 + 导航差异部分）

4.3 **配色原则（新增）**

frame_admin.html 及 frame.css 的所有颜色**优先且主要继承当前主题（default 或用户切换后的主题）**，不硬编码具体颜色值。

关键继承点：

- 背景色：var(--bg-body)、var(--bg-surface)、var(--bg-card)
- 文字色：var(--text-primary)、var(--text-secondary)、var(--text-muted)
- 导航栏背景：var(--bg-surface) 或 var(--bg-nav) 的变体
- 链接默认色：var(--text-secondary)
- 链接 hover 色：var(--text-primary) 或 var(--primary-light) 背景
- **选中状态（active）**：强烈建议使用 var(--primary) 系列
  - 背景：var(--primary-light) 或 rgba(var(--primary-rgb), 0.08~0.12)
  - 文字：var(--primary)
  - 左侧指示条：var(--primary) solid 4px
- 边框：var(--border-light) 或 var(--border)

**禁止**在 frame.css 中出现以下硬编码：
- #007bff、#0d6efd（Bootstrap 默认蓝）
- #f8f9fa、#343a40 等具体 hex 值

所有颜色必须通过 CSS 变量（--xxx）引用，确保与用户当前选择的主题（default / macaron / teal 等）保持一致。

### 5. 视觉与交互规范（更新）

- 左侧导航宽度：col-md-3 col-lg-2（约 16.7% ~ 25%）
- 右侧内容：col-md-9 col-lg-10
- 导航栏高度：vh-100 + overflow-auto
- 图标：Bootstrap Icons，fs-5，me-3
- 响应式：md 以下可后续考虑折叠

**线框草图（字符版）**  
（展示当右侧处于不同页面时，左侧对应菜单的选中状态）

```
┌───────────────────────────────────────────────────────────────┐
│                        系统管理                                 │
├───────────────┬───────────────────────────────────────────────┤
│  系统管理     │                                               │
│               │                                               │
│  ● 系统基本设置  ← active（背景浅主色 + 左侧4px主色条）      │
│    ─────────── │  ← 这里显示系统基本设置的表单或内容           │
│  ○ 人员管理   │                                               │
│               │                                               │
│               │                                               │
│               │                                               │
│               │                                               │
│               │                                               │
└───────────────┴───────────────────────────────────────────────┘
        20~25%               75~80%

┌───────────────────────────────────────────────────────────────┐
│                        系统管理                                 │
├───────────────┬───────────────────────────────────────────────┤
│  系统管理     │                                               │
│               │                                               │
│  ○ 系统基本设置                                              │
│    ─────────── │                                               │
│  ● 人员管理   ← active（背景浅主色 + 左侧4px主色条）         │
│               │  ← 这里显示用户列表 / 编辑用户表单等内容      │
│               │                                               │
│               │                                               │
│               │                                               │
└───────────────┴───────────────────────────────────────────────┘
        20~25%               75~80%
```

（● 表示当前选中状态，○ 表示未选中）

### 6. 子页面最小实现模板（不变）

```jinja
{% extends "frame_admin.html" %}

{% block title %}人员管理 - 列表{% endblock %}

{% set active_section = 'users' %}

{% block admin_content %}
  <h3 class="mb-4">人员管理</h3>
  <div class="card shadow-sm border-0">
    <div class="card-body">
      <!-- 表格或表单 -->
    </div>
  </div>
{% endblock %}
```

### 7. frame.css 推荐起始内容（更新，强调变量继承）

```css
/* static/css/frame.css */

/* ── 左侧导航 ──────────────────────────────────────── */
.admin-sidebar {
  background: var(--bg-surface);
  border-right: 1px solid var(--border-light);
  min-height: 100vh;
}

.admin-sidebar .nav-link {
  color: var(--text-secondary);
  padding: 0.75rem 1.25rem;
  border-radius: var(--radius-md);
  transition: background 0.2s, color 0.2s;
}

.admin-sidebar .nav-link:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.admin-sidebar .nav-link.active {
  background: var(--primary-light);
  color: var(--primary);
  font-weight: 500;
  border-left: 4px solid var(--primary);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}

/* ── 右侧内容区 ────────────────────────────────────── */
.admin-container {
  background: var(--bg-body);
}

main .h3, main .h2 {
  color: var(--text-primary);
}

/* 卡片在后台轻微强化边框（可选） */
.card {
  border-color: var(--border-light);
  border-radius: var(--radius-lg);
}
```

**策划书完（v1.1）**

如需进一步调整（例如增加返回仪表盘的图标样式、面包屑位置、或二级菜单预留结构），可以继续告诉我。
