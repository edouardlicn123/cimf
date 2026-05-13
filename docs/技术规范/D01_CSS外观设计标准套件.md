# CSS 外观设计标准套件

本文档定义 CIMF 项目中标准化的 CSS 外观设计模式。每个套件包含完整的设计规范、HTML 结构要求、CSS 规则及使用示例。

---

## 1. 基本卡片

基本卡片是 CIMF 中最通用的卡片设计，特点是**标题独立于卡片边框之外**，形成顶部圆角标签 + 底部直角边框容器的视觉风格。

```
    ╭──────────────╮
   │  基本设置      │   ← 标题标签（顶部圆角 6px，底部直角）
   │              │
   │  ┌──────────┐ │
   │  │  卡 片    │ │   ← 白色 card-body（primary 色 1px 边框）
   │  │  内 容    │ │
   │  └──────────┘ │
   └───────────────┘
```

### 用途

适用于系统设置页、用户管理页、模块编辑页的内容区块划分。

### HTML 结构规范

```html
<div class="card mb-3">
    <div class="card-header">
        <h5 class="mb-0"><!-- 可选图标 + 标题文本 --></h5>
    </div>
    <div class="card-body">
        <!-- 卡片内容 -->
    </div>
</div>
```

**要点：**
- `card-header` **不能**有 `bg-light` 类（否则标题背景会覆盖透明色）
- `card-header` **不能**有 `d-flex` 类（CSS 选择器 `:not(.d-flex)` 会排除）
- `h5` / `h4` 必须直接放在 `card-header` 内（可包含图标 `<i>`）
- `card-body` 默认使用 Bootstrap 标准 padding（1.25rem），特殊情况可追加 `p-0` 等

### CSS 规则

所有规则定义在 `static/css/frame.css` 中：

```css
/* ── 基本卡片 ── */

/* Card 容器：透明背景，无边框/阴影/圆角，
   让视觉边框完全交给 card-body */
.card:has(.card-header:not(.d-flex)) {
    background: transparent;
    border-radius: 0;
    box-shadow: none;
    border: none;
}

/* Card-body：白底 + primary 色边框，
    左上角无圆角（与标签底部衔接），其他三角为 --radius-sm */
.card:has(.card-header:not(.d-flex)) .card-body {
    background: var(--bg-card) !important;
    border-radius: 0 var(--radius-sm) var(--radius-sm) var(--radius-sm) !important;
    border: 1px solid var(--primary) !important;
    box-shadow: none !important;
    overflow: hidden;
}

/* Card-header：无底边线、透明背景、无 padding */
.card-header:not(.d-flex) {
    border-bottom: none;
    background: transparent;
    padding: 0;
}

/* 标题标签：跟随内容宽度、primary 色填充、白字、
   顶部圆角 6px、底部直角，形成标签感 */
.card-header:not(.d-flex) h5,
.card-header:not(.d-flex) h4 {
    display: inline-block;
    padding: 10px 32px 12px;
    margin: 0;
    background-color: var(--primary);
    color: white;
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: 0.04em;
    border-radius: 6px 6px 0 0;
    white-space: nowrap;
    line-height: 1.2;
}
```

### 使用说明

| 属性 | 值 | 说明 |
|------|----|------|
| 标题背景色 | `var(--primary)` | 跟随主题主色 |
| 标题文字色 | `white` | 与主色形成高对比 |
| 标题顶部圆角 | `6px` | 硬编码（不随 `--radius-sm` 变化） |
| 标题底部 | 直角 | 自然衔接到 card-body 边框 |
| Card-body 边框色 | `var(--primary)` | 与标题统一色调 |
| Card-body 圆角 | `0 --radius-sm --radius-sm --radius-sm` | 左上角为 0，与标签底部对齐 |
| Card-body `overflow` | `hidden` | 确保 `p-0` 时内层内容不遮挡圆角 |

### 已适配页面

- 系统设置（`admin/system_settings.html`） — 6 张卡片
- 权限管理（`admin/system_permissions.html`） — 3 张卡片
- 用户编辑（`admin/system_user_edit.html`） — 2 张卡片
- SMTP 配置（`smtp/config.html`） — 6 张卡片
- SMTP 历史（`smtp/history.html`） — 1 张卡片
- 日志查看（`admin/logs.html`） — 2 张卡片
- 权限检查（`admin/permission_check.html`） — 1 张卡片
- 模块创建（`module/modules/create.html`） — 1 张卡片
- 节点编辑（`node/edit.html`） — 1 张卡片
- 客户查看（`modules/customer/templates/view.html`） — 5 张卡片
- 客户编辑（`modules/customer/templates/edit.html`） — 5 张卡片
- 用户菜单设置（`usermenu/settings.html`） — 3 张卡片
- 用户菜单资料（`usermenu/profile.html`） — 3 张卡片
- 日志查看（`admin/logs.html`） — 2 张卡片

**合计：15 个文件，约 36 张卡片**

### 注意事项

1. **`!important` 的使用**：`.card-body` 的 `background`、`border-radius`、`border` 需加 `!important`，以覆盖各主题对 `.card-body` 的定制
2. **`bg-light` 冲突**：如果 `card-header` 仍有 `bg-light` 类，header 底色会遮住标签效果，需移除
3. **`d-flex` 排除**：`card-header` 上如有 `d-flex` 类（如需 header 内左右布局），会被 `:not(.d-flex)` 排除，不影响其原始样式
4. **`--radius-sm`**：在所有主题中定义为 4px，如需调整请在主题变量中统一修改
5. **`padding` 不使用 `!important`**：card-body 的 padding 由 Bootstrap 默认值控制，允许通过 `p-0` 等工具类覆盖
7. **`overflow: hidden`**：card-body 设置 `overflow: hidden`，确保使用 `p-0` 时内层内容不会溢出遮挡 `border-radius` 圆角
8. **图标支持**：h5 标题内可包含 `<i class="bi bi-xxx me-2"></i>`，间距由 `me-2` 控制

---

## 2. 基本过滤标签

基本过滤标签是一组**描边药丸按钮**，用于选择/过滤切换场景。非选中态为白底 + 主色边框/文字，选中态为主色填充 + 白字。

```
                         ╭──────────╮
  非选中：  ○ cimf 12KB  │  cimf   │   ← 主色 1px 边框 + 白底
                         │  12KB   │     主色文字 + 橙色大小标
                         ╰──────────╯

                         ╭──────────────╮
  选中：    ● cimf 12KB  │    cimf      │   ← 主色填充
                         │    12KB      │     白字 + 橙色大小标
                         ╰──────────────╯
```

### 用途

适用于导航式筛选、列表页的标签切换、日志文件选择等场景。目前用于日志管理页的日志文件选择器。

### HTML 结构规范

```html
<ul class="nav nav-pills nav-pills-outline flex-wrap gap-2">
    <li class="nav-item">
        <a class="nav-link active d-flex align-items-center" href="...">
            <i class="bi bi-file-earmark me-1"></i>
            标签名
            <span class="badge ms-2" style="background:#f57c00;color:#fff">数量</span>
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link d-flex align-items-center" href="...">
            ...
        </a>
    </li>
</ul>
```

**要点：**
- `<ul>` 必须有 `nav-pills-outline` 类（触发 CSS）
- 选中项 class 加 `active`
- 数量/大小等信息使用橙色 `<span class="badge">`（inline style `background:#f57c00;color:#fff`）

### CSS 规则

所有规则定义在 `static/css/frame.css` 中：

```css
/* ── 日志文件选择 - 描边药丸按钮 ── */
.nav-pills-outline .nav-link {
    background: #fff;
    border: 1px solid var(--primary);
    color: var(--primary);
    border-radius: 50px;
}
.nav-pills-outline .nav-link:hover {
    background: var(--primary-light);
}
.nav-pills-outline .nav-link.active {
    background: var(--primary);
    color: #fff !important;
}
.nav-pills-outline .nav-link.active .badge {
    background: rgba(255,255,255,.9);
    color: var(--primary);
}
```

### 使用说明

| 属性 | 非选中 | 选中 |
|------|--------|------|
| 背景色 | `#fff` | `var(--primary)` |
| 文字色 | `var(--primary)` | `#fff` |
| 边框 | `1px solid var(--primary)` | 同左（被填充覆盖） |
| 圆角 | `50px`（药丸形） | 同左 |
| Hover | `var(--primary-light)` | — |

### 已适配页面

- 日志管理（`admin/logs.html`） — 日志文件选择器

### 注意事项

1. **白色背景硬编码**：非选中态使用 `background: #fff`（非变量），因为 nav-link 默认无背景，需要固定白底覆盖各主题的按钮样式
2. **选中态 `!important`**：`.nav-link.active` 的 `color: #fff !important` 用于覆盖 Bootstrap `nav-pills` 的选中色
3. **橙色大小标**：文件大小使用硬编码色 `#f57c00`，未使用 CSS 变量；选中时 badge 变为半透明白底 + 主色文字
4. **Flex 布局**：标签内使用 `d-flex align-items-center` 确保图标、文字、badge 垂直居中
5. **badge 默认背景**：`bg-warning`（"不存在"状态）保留原始样式，不转为橙色
6. **gap 间距**：按钮间距由 `<ul>` 上的 `gap-2` 控制，可根据需要调整为 `gap-1`/`gap-3`

---

## 3. 基本列表

基本列表是一种**紧贴过滤栏下方的表格容器**，使用主色方角边框直接衔接上方的过滤标签，形成过滤 + 列表的完整区块。

```
  ┌──────┐ ┌──────┐ ┌──────┐
  │ cimf │ │error │ │sec..│  INFO 全部 ▼
  └──────┘ └──────┘ └──────┘
  ┌──────────────────────────────┐ ← 主色 1px 方角边框
  │  行号 │ 日志内容               │ ← 紧贴过滤标签
  │   1  │ 2026-05-09 INFO ...   │
  │   2  │ 2026-05-09 ERROR ...  │
  └──────────────────────────────┘
```

### 用途

适用于过滤标签下方的表格/列表区域，与基本过滤标签搭配使用。目前用于日志管理页的日志内容表格。

### HTML 结构规范

```html
<!-- 过滤栏 -->
<div class="d-flex align-items-end gap-2" style="margin-bottom:-1px">
    <ul class="nav nav-pills nav-pills-outline flex-wrap gap-2 mb-0">
        ...
    </ul>
    <div class="d-flex align-items-center gap-2 ms-auto">
        ...
    </div>
</div>

<!-- 列表容器 -->
<div class="log-table-wrap table-responsive">
    <table class="table table-hover mb-0">
        ...
    </table>
</div>
```

**要点：**
- 过滤栏使用 `align-items-end` 底部对齐 + `margin-bottom: -1px` 让过滤标签的底边框与列表的顶边框重叠
- 列表容器使用 `log-table-wrap table-responsive` 两个类
- 表格使用 `mb-0` 去除多余间距

### CSS 规则

所有规则定义在 `static/css/frame.css` 中：

```css
/* ── 日志表格边框 ── */
.log-table-wrap {
    border: 1px solid var(--primary);
}
```

### 使用说明

| 属性 | 值 | 说明 |
|------|----|------|
| 边框 | `1px solid var(--primary)` | 主色方角边框 |
| 圆角 | 无 | 方角，与过滤标签底角一致 |
| 间距 | 0（`margin-bottom:-1px` 重叠） | 紧贴上方过滤标签 |

### 已适配页面

- 日志管理（`admin/logs.html`） — 日志内容表格

### 注意事项

1. **过滤栏与列表的衔接**：过滤栏需设置 `align-items-end` 使所有元素底部对齐，并使用 `margin-bottom: -1px` 让两个元素的边框重叠，消除缝隙
2. **`table-responsive` 共存**：`log-table-wrap` 可与 `table-responsive` 同在一個 div 上实现水平滚动 + 边框
3. **表格自身**：表格需设置 `mb-0`，border 由 list 容器控制；如需水平和垂直边框，可使用 `table-bordered`

---

## 4. 基本按键

基本按键使用**渐变 `background-position` 扫描动画**：默认显示主色→稍暗渐变，悬停时渐变反向滑动，产生细腻的扫描效果。

```
默认：
┌──────────────────────┐
│  新建用户              │  ← 主色 ──→ 主色+暗色叠加
└──────────────────────┘

悬停（渐变反向扫描）：
┌──────────────────────┐
│  新建用户              │  ← 主色+暗色叠加 ──→ 主色
└──────────────────────┘
```

### 用途

适用于所有填充式操作按钮（新增、保存、删除、发送等）。不适用于描边式按钮（`btn-outline-*`）、次要按钮（`btn-secondary`）、以及独立动画的 entry-card 按钮。

### CSS 规则

所有规则定义在 `static/css/frame.css` 中：

```css
/* ── 基本按键：渐变滑动动画 ── */
.btn-primary,
.btn-success,
.btn-danger,
.btn-warning,
.btn-info {
    border: none !important;
    background-size: 200% 100% !important;
    background-position: 0% 0% !important;
    transition: background-position 0.4s ease, box-shadow 0.2s ease !important;
    box-shadow: none !important;
}

.btn-primary:hover,
.btn-primary:active,
.btn-primary.active,
.btn-success:hover,
.btn-success:active,
.btn-success.active,
.btn-danger:hover,
.btn-danger:active,
.btn-danger.active,
.btn-warning:hover,
.btn-warning:active,
.btn-warning.active,
.btn-info:hover,
.btn-info:active,
.btn-info.active {
    background-position: 100% 0% !important;
}

.btn-primary:focus-visible,
.btn-success:focus-visible,
.btn-danger:focus-visible,
.btn-warning:focus-visible,
.btn-info:focus-visible {
    outline: 2px solid var(--primary) !important;
    outline-offset: 2px !important;
}

.btn-primary {
    --btn-lighter: color-mix(in srgb, var(--primary), white 20%);
    background-image: linear-gradient(135deg, var(--btn-lighter) 0%, var(--primary) 30% 70%, var(--btn-lighter) 100%) !important;
    color: #fff !important;
}

.btn-success {
    --btn-lighter: color-mix(in srgb, var(--success), white 20%);
    background-image: linear-gradient(135deg, var(--btn-lighter) 0%, var(--success) 30% 70%, var(--btn-lighter) 100%) !important;
    color: #fff !important;
}

.btn-danger {
    --btn-lighter: color-mix(in srgb, var(--danger), white 20%);
    background-image: linear-gradient(135deg, var(--btn-lighter) 0%, var(--danger) 30% 70%, var(--btn-lighter) 100%) !important;
    color: #fff !important;
}

.btn-warning {
    --btn-lighter: color-mix(in srgb, var(--warning), white 20%);
    background-image: linear-gradient(135deg, var(--btn-lighter) 0%, var(--warning) 30% 70%, var(--btn-lighter) 100%) !important;
    color: #000 !important;
}

.btn-info {
    --btn-lighter: color-mix(in srgb, var(--info), white 20%);
    background-image: linear-gradient(135deg, var(--btn-lighter) 0%, var(--info) 30% 70%, var(--btn-lighter) 100%) !important;
    color: #fff !important;
}
```

### 技术原理

| 属性 | 值 | 说明 |
|------|----|------|
| `color-mix` | `color-mix(in srgb, COLOR, white 20%)` | 计算浅色变体（主色混 20% 白） |
| `background-image` | `linear-gradient(135deg, LIGHTER 0%, COLOR 30% 70%, LIGHTER 100%)` | 两色渐变：浅色→主色(占2/3可见区)→浅色，`30% 70%` 双位置停点表示主色区间 |
| `background-size` | `200% 100%` | 渐变宽度为容器 2 倍，仅一半可见 |
| `background-position` 默认 | `0% 0%` | 显示渐变左半（浅色→主色） |
| `background-position` 悬停 | `100% 0%` | 显示渐变右半（主色→浅色） |
| `transition` | `0.4s ease` | 平滑滑动 |

### 受影响的按钮色

| 按钮类 | 渐变色源 | 文字色 | 说明 |
|--------|----------|--------|------|
| `btn-primary` | `var(--primary)` | `#fff` | 主要操作（新增、保存） |
| `btn-success` | `var(--success)` | `#fff` | 成功/确认操作 |
| `btn-danger` | `var(--danger)` | `#fff` | 危险操作（删除） |
| `btn-warning` | `var(--warning)` | `#000` | 警告操作（暗色文字保证可读） |
| `btn-info` | `var(--info)` | `#fff` | 信息/查看操作 |

### 不受影响的范围

| 范围 | 原因 |
|------|------|
| `entry-card-actions` 内的按钮 | 独立更高优先级的选择器 `.entry-card-actions .btn`（0,2,1） |
| `btn-secondary` | 次要/取消按钮，保持低调 |
| `btn-outline-*` | 描边按钮，保持原样 |
| 登录页（`login.html`） | 独立硬编码的 `#0d6efd`，带 `!important` 保护 |

### HTML 用法

无需更改模板。所有现有的 `class="btn btn-primary"` 等自动获得动画效果。

```html
<!-- 保持不变 -->
<a href="..." class="btn btn-primary">新建用户</a>
<button class="btn btn-success">确认导入</button>
<button class="btn btn-danger">删除</button>
```

### 注意事项

1. **`!important` 的必须**：由于每个主题 CSS（如 `default.css`）使用 `!important` 定义按钮色，frame.css 必须在每行也使用 `!important` 来覆盖
2. **加载顺序**：frame.css 在主题 CSS 之后加载（见 `style.html`），确保 `!important` 声明的优先级
3. **动画衔接**：悬停与 active 状态共享相同的 `background-position: 100% 0%`，避免点击时闪回主题的纯色
4. **浅色变体**：使用 `color-mix(in srgb, COLOR, white 20%)` 计算比主色浅 20% 的色调，确保所有颜色变体一致地显示「浅→主色」两色渐变
5. **`background-image` 而非 `background`**：使用 `background-image` 单独设置渐变，不会覆盖公共块中的 `background-size` 和 `background-position`，确保动画生效
6. **`30% 70%` 双位置停点**：`primary 30% 70%` 表示主色从 30% 开始、70% 结束，中间为实色。在 `background-size: 200%` 下每边可见 50% 渐变，主色占可见区 40%/50%=80%，过渡区各占 10%/50%=20%
7. **`focus-visible`**：使用 `outline` 替代 `box-shadow` 作为焦点指示，避免与背景渐变的 `box-shadow` 冲突
8. **无 `border-radius` 覆盖**：按钮圆角继承 Bootstrap 默认值（`0.375rem`），不与 `--radius-sm` 绑定，保持灵活
9. **登录页保护**：`login.html` 内联样式添加了 `!important` 和 `background-image: none`，确保登录按钮不受 frame.css 影响
10. **Bootstrap 4/5 兼容**：此方案依赖于 `background-size` 和 `background-position`，两者在 Bootstrap 4 和 5 中均无冲突覆盖
11. **`color-mix()` 浏览器支持**：`color-mix()` 是 CSS Color Level 5 函数，支持所有现代浏览器（Chrome 111+, Firefox 113+, Safari 16.2+）。不支持 `color-mix()` 的浏览器会跳过整个 `background` 声明，回退到主题的 `background-color` 纯色按钮，功能不受影响

---

## 5. 首页卡片

首页卡片适用于仪表盘中的功能入口卡片（快捷入口）和常用链接卡片。设计强调**深色背景上的白色半透明内发光**，hover 时浮现柔和光晕，无升起效果。

```
默认：
┌──────────────────────┐
│                      │
│   客户信息            │  ← 纯色背景（primary 或 primary-light）
│   150                 │
│   本周新增 5 条       │
│                      │
└──────────────────────┘

Hover（白色半透明内发光）：
┌──────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░ │  ← inset box-shadow
│ ░░  客户信息      ░░ │     白色半透明层叠在背景之上
│ ░░  150          ░░ │
│ ░░  本周新增 5 条 ░░ │
│ ░░░░░░░░░░░░░░░░░░░░ │
└──────────────────────┘
```

### 用途

- 快捷入口的 6 张功能卡片（`.module-card`）
- 常用链接的 12 张导航卡片（`.nav-card`）

### 受影响的 CSS 类

| 类名 | 所在文件 | 说明 |
|------|----------|------|
| `.module-card` | `includes/dashboard_cards_area.html` | 功能卡片（inline style） |
| `.nav-card` | `includes/nav_cards_area.html` | 导航卡片（inline style） |

### CSS 规则

所有规则以内联 `<style>` 形式写在对应模板文件中：

```css
/* 功能卡片 hover */
.module-card:hover {
    box-shadow: inset 0 0 0 1px #fff;
}

/* 导航卡片 hover */
.nav-card:hover {
    box-shadow: inset 0 0 0 1px #fff;
    color: #fff;
}
```

### 技术原理

| 属性 | 值 | 说明 |
|------|----|------|
| `box-shadow` | `inset 0 0 0 1px #fff` | `inset` + `0 0 0`（无模糊）+ `1px` 扩展半径，形成纯白色内边框线 |
| 颜色 | `#fff` | 白色不透明 |
| 线框宽度 | `2px` | 清晰可见的白色边框 |
| `transform` | 无 | 明确不升起，保持卡片平面感 |

### 使用说明

1. **可见性依赖背景色**：白色内发光在深色背景上最为明显（`var(--primary)`、`var(--primary-light)` 或自定义 `bg_color`），浅色背景上效果较弱
2. **`inset` 不干扰外阴影**：内发光与外阴影独立共存，如卡片本身有 `box-shadow` 外阴影，hover 时不会被覆盖
3. **`color: #fff` 保持**：导航卡片 hover 时文字色保持白色，不被内发光影响
4. **过渡动画**：利用原有 `.module-card` / `.nav-card` 上的 `transition` 属性即可平滑显现内发光（已定义 `transition: transform 0.2s ease, box-shadow 0.2s ease`），无需额外声明

### 注意事项

1. **与现有阴影兼容**：`.module-card` 默认有 `box-shadow: var(--shadow)`，hover 时被 `inset` 替换。如需要同时保留外阴影，应使用 `box-shadow: var(--shadow), inset 0 0 0 1px #fff`（用逗号分隔多层阴影）
2. **与主题变量无关**：内线框颜色固定为白色，不依赖任何 CSS 变量，在所有主题中表现一致
3. **仅影响 hover**：默认态和 active/grabbing 等状态不受影响，保持原有样式
4. **升序选择器顺序**：`.module-card:hover` 必须定义在同文件 `.module-card` 之后，确保优先级正确
5. **导航卡片 `color`**：`.nav-card:hover` 中的 `color: #fff` 用于覆盖可能的外链默认色（如 `a` 标签的蓝色），确保 hover 时文字不跳色

---
