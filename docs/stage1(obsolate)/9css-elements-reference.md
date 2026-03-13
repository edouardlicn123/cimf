# FFE 项目跟进系统 - CSS 元素参考列表（更新版 2026-02-13）

**更新日期**：2026-02-13  
**已覆盖主题**：default（领英）、macaron（马卡龙）、dopamine（多巴胺）、teal（青绿专业）、uniklo（优衣库极简）  
**核心修复进度**：
- 宽屏右侧用户下拉菜单完整显示（v6 方案，所有主题统一）
- dashboard 卡片强制等宽（320px + card-body 100% 撑满 + 按钮贴底，所有主题同步）
- 卡片按钮跟随主题颜色（primary/success/info，通用规则）
- 导航栏除用户菜单外字体加粗（品牌 + 仪表盘链接）
- 卡片风格参考 uniqlo 极简优化（圆角收窄、阴影轻微、hover 克制）

## 1. 全局通用元素

| CSS 选择器 / Class              | 典型用途                             | 常见主题变量依赖                          | 备注 / 建议 |
|--------------------------------|--------------------------------------|--------------------------------------------|-------------|
| body                           | 整体背景、字体、文字色               | --bg-gradient, --bg-body, --text-primary   | 统一 min-height: 100vh |
| main.container                 | 主内容容器（白色底 + 边框 + 圆角）   | --bg-card, --border / --border-light, --radius-lg, --shadow | 所有页面内容包裹层 |
| .container                     | Bootstrap 响应式容器                 | —                                          | 基本不加额外样式，由主题控制 max-width |
| .card                          | 通用卡片（dashboard、settings、profile） | --bg-card, --shadow, --radius-lg / --radius-xl | 常加 shadow-sm / border-0，最新修复固定 320px |
| **.card-body**                 | 卡片内部内容容器                     | --bg-card, padding 统一 1.5rem/1rem 或 2rem/1.5rem | **强制 width: 100% !important; height: 100% !important;** 确保撑满卡片 + 按钮贴底 |
| .card-entry                    | dashboard 快速入口卡片               | --shadow / --shadow-hover, --radius-lg / 4px（uniqlo参考） | hover 时 translateY(-2px) + shadow-hover（极简版） |
| .card-btn                      | dashboard / 欢迎栏按钮               | --primary / --success / --info, --radius-pill | 跟随主题颜色（primary-btn / success-btn / info-btn） |
| .btn-info, .settings-btn, .edit-btn | 保存/提交/编辑按钮             | --info, --info-hover, --radius-pill        | 表单提交通用 |
| .accordion-button              | 设置/个人中心折叠标题                | --primary (展开时), --bg-surface (折叠时) | not(.collapsed) 时背景变主色 |
| .dropdown-menu                 | 导航栏个人下拉菜单                   | --bg-card, --border-light, --shadow-sm     | dropdown-menu-end + shadow |
| .alert-warning, .password-warning | 警告提示框                     | --warning-light, --warning                 | 密码修改 / 弱密码提醒 |
| .badge                         | 角色/状态标签                        | --radius-sm                                | bg-success / bg-danger / bg-info |
| .avatar-placeholder            | 头像占位符                           | --border, hover --primary / --info         | 圆形 + scale(1.08) hover |

## 2. 导航栏相关（includes/nav.html）

| CSS 选择器 / Class              | 典型用途                             | 主题变量依赖                               | 备注 |
|--------------------------------|--------------------------------------|--------------------------------------------|------|
| .navbar-macaron                | 整个导航栏容器                       | --bg-nav, --shadow-nav, --radius-lg        | fixed-top + border-bottom |
| .navbar-macaron .nav-link      | 导航链接（仪表盘）                   | --text-nav, --text-nav-active              | fw-bold（粗体） |
| .navbar-macaron .navbar-brand  | 左侧品牌名称                         | --text-nav                                 | fw-bold + fs-4 |
| .navbar-macaron .collapse.navbar-collapse | 展开的内容区（手机端）         | 强制 transparent / 无 border & shadow      | 已修复透明 |
| .navbar-macaron .dropdown-menu | 个人下拉菜单                         | --bg-card, --border-light, --shadow-sm     | dropdown-menu-end |
| .navbar-macaron .login-btn     | 未登录时的“登录”按钮                 | border & color = white / --primary         | rounded-pill + btn-sm |
| .navbar-macaron .logout-link   | 退出登录链接                         | color: --danger                            | bi-box-arrow-right 图标 |

## 3. 页面特定元素

| Class / 选择器                 | 页面                                 | 用途                                       | 主题变量依赖 |
|--------------------------------|--------------------------------------|--------------------------------------------|--------------|
| .welcome-title                 | dashboard                            | “欢迎回来，xxx！”                         | color: --primary |
| .welcome-bar                   | dashboard                            | 欢迎信息栏（含边框）                       | border-bottom |
| .quick-actions                 | dashboard                            | 右侧“新建项目”“刷新”按钮组                | gap-2 |
| .dashboard-cards               | dashboard                            | 快速入口卡片容器                           | d-flex flex-wrap justify-content-center gap-4 |
| .card-icon                     | dashboard                            | 卡片图标（bi-calculator 等）               | color: --primary |
| .system-status                 | dashboard                            | 系统状态提示 alert                         | alert-info + rounded-3 + shadow-sm |
| .settings-title                | settings                             | “系统设置”标题                             | color: --primary |
| .settings-card                 | settings                             | 设置项卡片                                 | --radius-lg, --shadow |
| .settings-btn                  | settings                             | 保存按钮                                   | 与 .btn-info 共用 |
| .profile-title                 | profile                              | “个人中心”标题                             | color: --primary |
| .password-warning              | settings / profile                   | 修改密码警告框                             | --warning-light 背景 |

## 4. 其他高频工具类 / 状态类

| Class                          | 用途                                 | 建议主题处理方式 |
|--------------------------------|--------------------------------------|------------------|
| .text-primary                  | 强调主色文字                         | color: --primary |
| .text-muted                    | 辅助说明文字                         | color: --text-muted |
| .fw-bold                       | 加粗文字（导航品牌、仪表盘链接）     | font-weight: bold |
| .fw-medium                     | 卡片标题                             | font-weight: 500 |
| .form-text.text-muted.small    | 输入框下方说明文字                   | color: --text-muted, small |
| .form-select, .form-control    | 下拉框、输入框                       | focus 边框 --border-focus |
| .alert.alert-info              | 系统状态提示                         | --info-light 背景 |
| .btn-outline-secondary         | 次要操作按钮                         | border & color 用 --text-muted / --primary-light |

## 5. 已确认主题文件命名与风格（更新）

| 主题英文名     | 文件名              | 显示名称（下拉菜单用）               | 风格描述 | 卡片宽度 | 卡片圆角 | 卡片阴影 | hover 效果 | 卡片按钮跟随主题 |
|----------------|---------------------|---------------------------------------|----------|----------|----------|----------|------------|------------------|
| default        | default.css         | 默认（领英风格）                      | 专业、干净、现代企业 | 320px | 6-8px | 中等 | scale 1.04 + translateY | 是 |
| macaron        | macaron.css         | 马卡龙甜点风                          | 柔和糖果色、可爱治愈 | 320px | 4-6px | 极轻 | translateY(-2px) | 是 |
| dopamine       | dopamine.css        | 多巴胺活力风                          | 高饱和、明亮、快乐奖励感 | 320px | 8-12px | 活泼 | scale 1.04 + translateY(-12px) | 是 |
| teal           | teal.css            | 青绿专业风                            | 清新现代、医院/环保感 | 320px | 4-8px | 克制 | box-shadow-hover | 是 |
| uniklo         | uniklo.css          | 优衣库极简风                          | 干净直线条、经典红白 | 320px | 0-4px | 极轻 | 无或轻微上移 | 是 |

**新增建议**  
- **.card-body**：所有卡片内部内容容器，最新修复已强制 `width: 100% !important; height: 100% !important;` + `box-sizing: border-box`，确保撑满卡片 + 按钮贴底。新模板中优先使用 `.card-body` 而不是自定义 div。
- 新增卡片时：外层加 `.dashboard-cards`（或类似 `.xxx-cards`），内部卡片加 `.card-entry`，按钮加 `.card-btn + primary-btn / success-btn / info-btn`
- 按钮文字颜色：统一 white（高对比），背景使用主题变量
- 卡片标题：统一 `.card-title fw-medium`


