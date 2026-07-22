# CSS 外观设计标准套件

标准化 CSS 外观设计模式。每套件含设计规范、HTML 结构、CSS 规则及示例。

---

## 1. 基本卡片

标题独立于卡片边框之外，顶部圆角标签 + 底部直角边框容器。

### 用途

系统设置页、用户管理页、模块编辑页的内容区块划分。

### HTML 结构

`<div class="card mb-3">` → `<div class="card-header"><h5 class="mb-0">` → `<div class="card-body">`

**要点：** `card-header` 不能有 `bg-light` 或 `d-flex`；`h5`/`h4` 直接放 header 内。

### CSS 规则

`static/css/frame.css` — `.card:has(.card-header:not(.d-flex))`

### 使用说明

| 属性 | 值 | 说明 |
|------|----|------|
| 标题背景色 | `var(--primary)` | 跟随主题主色 |
| 标题文字色 | `white` | 高对比 |
| 标题顶部圆角 | `6px` | 不随 `--radius-sm` 变 |
| 标题底部 | 直角 | 衔接 card-body |
| Card-body 边框色 | `none` | 基础卡片无边框 |
| Card-body 圆角 | `0 0 var(--radius) var(--radius)` | 仅底部圆角 |
| Card-body `overflow` | `hidden` | 防内容溢出 |
| 卡片整体边框 | `none` | 基础卡片无边框 |

### CSS 变体

| 变体类名 | Card-body 边框 | Card-body 背景 | 用途 |
|----------|---------------|---------------|------|
| 基础（无变体） | `none` | 由 `.card` 的 `bg-card` 决定 | 默认，边框由标题色线间接指示 |
| `.card-structure` | `1px solid var(--primary)` | `var(--bg-card)` | 显式主色边框，适用于需要明确区块分隔的页面 |
| `.card-structure-transparent` | 无，配合 `.card-body-border` | `transparent` | 透明背景，配合独立的 `.card-body-border` 容器，用于结构列表页 |

### 已适配页面

15 文件 ~36 卡片（system_settings、permissions、user_edit、logs 等）

### 注意事项

1. `!important` 用于 card-body 的 background/border-radius/border
2. 移除 header 的 `bg-light`；`:not(.d-flex)` 保护 flex 布局
3. `--radius-sm` 默认 4px，统一在主题变量修改
4. `padding` 不用 `!important`，允许 `p-0` 覆盖
5. `overflow: hidden` 防 `p-0` 时内容溢出圆角
6. 图标：`<i class="bi bi-xxx me-2"></i>` 嵌入 h5

---

## 2. 基本过滤标签

描边药丸按钮：非选中白底+主色边框/文字，选中主色填充+白字。

### 用途

导航式筛选、列表页标签切换。目前用于日志管理页。

### HTML 结构

`<ul class="nav nav-pills nav-pills-outline flex-wrap gap-2">` → `<a class="nav-link active d-flex align-items-center">`

**要点：** `<ul>` 需 `nav-pills-outline`，选中项加 `active`，badge 用 `#f57c00`。

### CSS 规则

`static/css/frame.css` — `.nav-pills-outline`

### 使用说明

| 属性 | 非选中 | 选中 |
|------|--------|------|
| 背景色 | `var(--bg-surface)` | `var(--primary)` |
| 文字色 | `var(--primary)` | `var(--text-inverse)` |
| 边框 | `1px solid var(--primary)` | 同左 |
| 圆角 | `6px 6px 0 0`（仅顶部） | 同左 |
| Hover | `var(--primary-light)` | — |

### 注意事项

1. 非选中 `background: var(--bg-surface)`（跟随主题）；选中 `color: var(--text-inverse) !important`
2. 橙色 badge `#f57c00`；选中时变半透明白底+主色
3. 标签内 `d-flex align-items-center`；`gap-2` 控制间距
4. `bg-warning` badge 保留原始样式

---

## 3. 基本列表

紧贴过滤栏下方的表格容器，主色方角边框直接衔接上方过滤标签。

### HTML 结构

过滤栏：`<div class="d-flex align-items-end gap-2" style="margin-bottom:-1px">` + `<div class="log-table-wrap table-responsive">` + `<table class="table table-hover mb-0">`

**要点：** `align-items-end` + `margin-bottom:-1px` 重叠边框消除缝隙。

### CSS 规则

`static/css/frame.css` — `.log-table-wrap`

### 使用说明

| 属性 | 值 |
|------|----|
| 边框 | `1px solid var(--primary)` |
| 圆角 | 无（方角） |
| 间距 | `margin-bottom:-1px` 紧贴过滤栏 |

### 已适配页面

日志管理（`admin/logs.html`）

### 注意事项

表格设 `mb-0`，border 由容器控制；可与 `table-responsive` 共存。

---

## 4. 基本按键

渐变 `background-position` 扫描动画：默认主色→稍暗渐变，悬停反向滑动。

### 用途

填充式操作按钮（新增、保存、删除、发送等）。`.btn-secondary` 仅参与 `border: none !important`，不参与渐变扫描动画。不适用：`btn-outline-*`、entry-card 按钮。

### CSS 规则

`static/css/frame.css` — `.btn-primary, .btn-secondary, .btn-success, .btn-danger, .btn-warning, .btn-info`（边框去除）；`.btn-primary, .btn-success, .btn-danger, .btn-warning, .btn-info`（渐变动画）

### 技术原理

| 属性 | 值 |
|------|----|
| `color-mix` | `color-mix(in srgb, COLOR, white 20%)` |
| `background-image` | `linear-gradient(135deg, LIGHTER 0%, COLOR 30% 70%, LIGHTER 100%)` |
| `background-size` | `200% 100%` |
| `background-position` 默认/悬停 | `0% 0%` / `100% 0%` |
| `transition` | `0.4s ease` |

### 受影响的按钮色

`btn-primary`(primary/#fff), `btn-success`(success/#fff), `btn-danger`(danger/#fff), `btn-warning`(warning/#000), `btn-info`(info/#fff)

### 注意事项

1. `!important` 必须 — frame.css 在主题 CSS 后加载覆盖
2. 悬停与 active 共享 `background-position: 100% 0%` 防闪回
3. 用 `background-image` 而非 `background`，不覆盖 size/position
4. `30% 70%` 双位置停点 — 主色占可见区 ~80%
5. `focus-visible` 用 `outline` 替代 `box-shadow`
6. 无 `border-radius` 覆盖，继承 Bootstrap 默认
7. 登录页内联 `!important` + `background-image: none` 保护
8. `color-mix()` 支持 Chrome 111+, Firefox 113+, Safari 16.2+

---

## 5. 首页卡片

仪表盘功能入口卡片：深色背景上白色半透明内发光，hover 柔和光晕，无升起。

### 用途

快捷入口 6 张功能卡片（`.module-card`）+ 常用链接 6 张导航卡片（`.nav-card`）

### CSS 规则

内联 `<style>` 在对应模板中：`.module-card:hover { box-shadow: inset 0 0 0 1px #fff; }`

### 技术原理

| 属性 | 值 |
|------|----|
| `box-shadow` | `inset 0 0 0 1px #fff` |
| `transform` | 无（不升起） |

### 使用说明

1. 深色背景效果最明显；`inset` 与外阴影可逗号分隔共存
2. `.nav-card:hover` 加 `color: #fff` 防文字跳色
3. 利用已有 `transition: box-shadow 0.2s ease` 平滑显现

### 注意事项

1. 保留外阴影：`box-shadow: var(--shadow), inset 0 0 0 1px #fff`
2. 内线框固定 `#fff`，不依赖 CSS 变量
3. 仅影响 hover；`.module-card:hover` 定义在同文件 `.module-card` 之后

---
