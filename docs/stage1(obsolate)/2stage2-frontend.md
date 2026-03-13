# FFE 项目跟进系统 - 前端模板与样式体系改造方案（最新确认版）

此方案基于前期讨论，结合前端页面结构优化（base.html + 可控 nav + header/footer + flash）和 CSS 现代化需求（路径 B、管理后台风格、默认主色 #2563eb、多主题架构能力）。方案旨在将当前零散、Bootstrap 类名主导的结构升级为清晰、可维护、可扩展的体系，同时保持开发效率。

## 1. 总体目标

1. 建立统一的视觉语言，风格偏向现代、专业的管理后台（清晰、高效、可读性强、长时间使用舒适）。
2. 默认主色调采用 #2563eb（明亮科技蓝），并保留后续添加其他主题的能力（深蓝、靛蓝、青绿、灰蓝、暗色模式等）。
3. 实现模板结构与样式的清晰分层，减少重复代码，提高可维护性。
4. 导航栏显示/隐藏可控（登录页等公共页面不显示 nav）。
5. 逐步减少对 Bootstrap 类名的硬依赖，核心组件样式由自定义变量驱动。
6. 为后续可能的暗色模式、个性化主题、客制化皮肤预留空间。

## 2. 模板结构目标状态

```
app/templates/
├── base.html                     # 唯一的基础模板（骨架 + 公共结构）
├── includes/
│   ├── header.html               # 系统标题 / logo / 全局头部（可带登录状态）
│   ├── nav.html                  # 主导航栏（当前建议保持顶部）
│   ├── footer.html               # 底部版权、版本信息
│   ├── flash_messages.html       # flash 消息统一渲染块
│   ├── style.html                # 统一承载所有 CSS 链接（Bootstrap + custom + 主题）
│   └── js.html                   # 统一承载所有 JS 脚本（Bootstrap + custom）
```

**核心原则**：所有页面都直接继承 `base.html`，通过变量控制区域显示/隐藏（主要是 nav）。CSS 和 JS 的引入全部集中到 `includes/style.html` 和 `includes/js.html`。

## 3. 模板层级与控制机制

- **base.html** 职责：
  - html / head / body 基本结构。
  - 在 `<head>` 中：`{% include "includes/style.html" %}`。
  - 在 `<body>` 末尾：`{% include "includes/js.html" %}`。
  - 包含 header、nav（条件）、main、footer。
  - 提供常用 block：title、head_extra、content、scripts。

- **控制导航栏显示的关键机制**：
  在 base.html 中使用：
  ```
  {% if show_nav|default(true) %}
      {% include "includes/nav.html" %}
  {% endif %}
  ```
  子模板（例如登录页）只需在顶部写：
  ```
  {% set show_nav = false %}
  ```
  其他页面不写任何 set 语句，默认显示导航栏。

- **是否需要控制 header 或 footer？**  
  当前建议：暂时不需要（header 和 footer 在登录页也保留较为友好），未来如有打印页、无边框页等需求再增加类似 `show_header`、`show_footer` 变量。

- **CSS 统一管理**：所有 CSS 链接都放在 `includes/style.html` 中，例如：
  - Bootstrap CDN。
  - custom.css。
  - 动态主题文件（default.css 或其他）。

- **JS 统一管理**：所有 script 标签都放在 `includes/js.html` 中，例如：
  - Bootstrap bundle。
  - 自定义 common.js。
  - 其他可能的库或内联脚本。

## 4. CSS 体系设计

**文件结构（最终状态）**

```
app/static/css/
├── custom.css                    # 唯一入口（系统自定义样式 + @import 主题）
├── base.css                      # 结构、布局、组件通用规则（开头包含 reset/normalize 内容 + 大量使用变量）
└── themes/
    ├── variables.css             # 变量声明（:root { --var-name: ; }，不赋值）
    ├── default.css               # 默认主题（主色 #2563eb）
    ├── deep-blue.css             # #1d4ed8
    ├── indigo.css                # #1e40af
    ├── teal.css                  # #0f766e
    ├── slate.css                 # #334155
    └── dark.css                  # 暗色模式（未来）
```

**custom.css 典型内容顺序**（建议）：
- 变量声明（@import './themes/variables.css'）。
- 通用基础样式、组件、布局（@import './base.css'，其中开头合并 reset 规则）。
- 当前主题（@import './themes/default.css'）。

**在模板中引入方式**（includes/style.html 示例）：
```
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
<link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
```

**加载方式（中期目标，支持动态主题）**：
```
<link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">

<link 
  rel="stylesheet" 
  href="{{ url_for('static', filename='css/themes/' ~ (current_theme or 'default') ~ '.css') }}" 
  id="theme-link"
>
```

## 5. 视觉风格与规范（管理后台导向）

**默认主题关键设定**

- 主色：#2563eb（科技蓝）。
- 主色交互态：hover #1d4ed8，active #1e3a8a，focus ring rgba(37,99,235,0.2)。
- 成功绿：#10b981。
- 警告黄：#f59e0b。
- 危险红：#ef4444。
- 页面背景：#f8f9fc 或 #fafafa。
- 卡片/表面：#ffffff。
- 边框：#e2e8f0。
- 文字主色：#111827。
- 文字次色：#475569 / #6b7280。
- 圆角：主要 6px，部分小组件 4px，大区域可选 8px。
- 阴影：轻到中（sm ~ md 级别）。
- 间距：4px 倍数系统（4/8/12/16/20/24/32/40/48/64）。
- 字体：PingFang SC / Helvetica Neue / Arial / sans-serif。
- 字号层级：12px（辅助）、14px（正文）、16px（base）、18px、20px、24px（标题）。

**组件风格基调**

- 按钮：实色填充 + 6–8px 圆角 + 中等 padding。
- 输入框：细边框 + focus 蓝色外环 + 背景白色。
- 卡片：白色底 + 细边框 + 轻阴影 + 6–8px 圆角。
- 表格：有横向分割线 + 可选斑马纹 + 表头浅灰底。
- 导航栏：深蓝或白色底 + 高对比文字 + 当前项高亮（背景或下划线）。

## 6. 实施分阶段计划（建议顺序）

**阶段 1 – 基础准备（最优先）**  
- 创建 themes/variables.css（只声明变量）。  
- 创建 themes/default.css（给变量赋值 + 少量覆盖规则）。  
- 创建或更新 base.css（开头合并 reset/normalize 规则 + 通用组件样式）。  
- 创建 includes/style.html 和 includes/js.html（统一 CSS/JS 引入）。

**阶段 2 – 模板结构优化**  
- 重构 base.html 为单一骨架 + 条件渲染 nav。  
- 抽取 header / nav / footer / flash_messages 到 includes/。  
- 修改登录页使用 `{% set show_nav = false %}`。  
- 修改其他页面（dashboard、project 等）保持默认显示 nav。

**阶段 3 – 页面逐步套用**  
- 优先改造：登录页（视觉影响最大，用户第一印象）。  
- 次优先：仪表盘（核心入口页）。  
- 然后：项目列表、项目详情、创建/编辑页。

**阶段 4 – 主题与扩展准备（完整建议版）**  
这一阶段的目标是在默认主题（以 #2563eb 为主色）稳定运行后，系统性地引入多主题支持能力，为未来不同使用场景、用户偏好、部门定制、品牌客制化、护眼需求等预留空间。

#### 4.1 推荐的主题色方案清单（全部纳入）

以下是建议纳入系统的全部主题色方案，每个主题都有明确的定位和适用场景：

| 主题名称       | 主色 (Primary) | 建议色值       | 风格描述                           | 适用场景建议                              | 优先级 |
|----------------|----------------|----------------|------------------------------------|-------------------------------------------|--------|
| default        | 科技蓝         | #2563eb        | 明亮、现代、活力适中               | 系统默认主题，大多数日常使用场景          | ★★★★★（最高） |
| deep-blue      | 深邃蓝         | #1d4ed8        | 沉稳、专业、权威感强               | 正式企业内部系统、财务/管理层后台        | ★★★★☆ |
| indigo         | 靛蓝           | #1e40af        | 冷调、高端、专注                   | 设计感较强的管理后台、产品/研发部门      | ★★★★☆ |
| teal           | 青绿           | #0f766e        | 清新、专业、现代医疗/环保感        | 健康、环保、酒店运营相关模块             | ★★★☆☆ |
| slate          | 深灰蓝灰       | #334155        | 中性、低调、极简、数据导向         | 数据分析、报表、长时间盯屏场景            | ★★★☆☆ |
| dark           | 暗色主色       | #2563eb（或微调） | 护眼、夜间友好、高对比             | 夜间/长时间使用、用户手动切换偏好        | ★★★★☆（强烈推荐） |
| high-contrast  | 高对比黑白基调 | #000000 / #ffffff 主导 | 极高对比度、无障碍优化             | 视力较弱用户、强光环境、合规要求场景      | ★★☆☆☆（可选） |

**说明**：
- 以上 7 个主题是当前阶段建议**全部纳入规划**的颜色方案。
- 其中 **default** 是必须最先实现的主题。
- **dark** 建议作为第二个重点实现（用户需求普遍较高）。
- 其他主题（deep-blue、indigo、teal、slate）可按需分批实现，先做 1～2 个验证架构即可。
- high-contrast 可作为无障碍支持的补充，不必急于实现。

#### 4.2 主题实现与管理方式建议

- **存储方式**  
  用户表（User 模型）增加字段：`theme`（字符串，默认值 'default'）。

- **加载方式**（推荐两种并行支持）  
  1. 静态加载（短期最简单）  
     在 base.html 中固定引入 custom.css，custom.css 最后 @import 当前主题。  
  2. 动态加载（中期目标）  
     使用单独的 `<link id="theme-link">` 标签，href 指向 `/static/css/themes/${theme}.css`。

- **主题切换入口建议**  
  - 管理员设置页面（/admin/settings）。  
  - 用户个人设置页面（/settings 或 /profile）。  
  - 开发调试快捷入口（dashboard 右上角隐藏下拉，仅 debug 模式或 admin 可见）。

- **主题文件组织规范**  
  每个主题文件（default.css、dark.css 等）应尽量只包含：
  - 变量重新赋值（:root { --color-primary: ... }）。
  - 极少量必须的覆盖规则（例如某些组件在该主题下需要特别调整的 hover/active 效果）。
  - 禁止在主题文件中写大量结构或布局规则。

#### 4.3 主题开发优先顺序建议

1. default（#2563eb） → 必须完成，作为系统主视觉。
2. dark → 强烈推荐尽快实现，用户接受度最高。
3. deep-blue（#1d4ed8） → 作为第二个彩色主题验证。
4. indigo（#1e40af）或 teal（#0f766e） → 选一个继续验证。
5. slate（#334155） → 可延后。
6. high-contrast → 根据无障碍需求决定是否实现。

#### 4.4 主题扩展的长期可能性

- 支持用户自定义主题（上传或编辑少量变量）。
- 支持部门/项目级主题（不同项目组使用不同配色）。
- 支持品牌客制化（为特定客户部署时更换主色）。
- 支持季节/活动主题（短期活动使用特殊配色）。
- 支持 A/B 测试（部分用户随机分配不同主题，收集使用反馈）。

## 7. 注意事项与风险点

- Bootstrap 5 兼容性：尽量保留 grid、modal、dropdown 等功能，但颜色、按钮、表格等逐步用自定义样式覆盖。
- 迁移成本：建议分页面逐步替换，不要一次性全部改动。
- 暗色模式：建议作为独立主题实现，而不是 media query（更灵活，可手动切换）。
- 性能：CSS 文件不宜过大，主题文件只包含变量赋值和少量规则。
- 测试重点：长时间阅读表格、表单填写、列表浏览场景下的舒适度。

## 8. 整体时间估算与资源需求

- 阶段 1–3：1–2 周（核心改造）。  
- 阶段 4：1 周（扩展准备）。  
- 总资源：1–2 名前端开发（Flask + Jinja 经验）；测试设备（桌面/移动/不同浏览器）。  
- 预算考虑：免费工具为主（如 VS Code、Lighthouse），无额外成本。

## 9. 成功指标

- 主题切换时间 < 1s，无闪屏。  
- 页面加载时间 < 2s（Chrome DevTools 审计）。  
- 用户反馈：视觉舒适度 > 4/5（内部测试）。  
- 代码覆盖：所有视觉属性 100% 使用变量。
