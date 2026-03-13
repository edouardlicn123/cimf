以下是根据你的最新要求更新后的策划书（版本 1.3），模板文件名全部采用 `system_` 前缀的命名规则：

- 系统设置页面：`system_general.html`
- 用户列表页面：`system_userslist.html`
- 用户新建/编辑页面：`system_useredit.html`

并保持其他内容一致。

# FFE 项目跟进系统 - 系统管理模块（第一阶段）策划书 v1.3

**文档版本**：1.3  
**更新日期**：2026年2月13日  
**当前阶段目标**：实现「系统设置」（单页）与「用户管理」两大功能模块  
**核心约束**：

- 仅使用两个独立蓝图：`settings_bp` 与 `users_bp`
- 路径前缀固定为 `/settings` 与 `/users`
- 系统设置所有内容合并为**单个页面**
- 用户新建与编辑共用同一页面模板（通过条件渲染区分）
- 用户**无删除功能**，仅支持启用/禁用（放在编辑页面内）
- 所有系统级配置统一存储在数据库 `Config` 表（key-value 结构）
- 左侧导航在对应蓝图路径下保持稳定高亮
- **模板文件统一前缀**：`system_`

## 1. 路由规划

| 蓝图          | url_prefix | 主要路由                              | HTTP 方法 | 功能描述                              | 模板文件建议                        | 优先级 |
|---------------|------------|---------------------------------------|-----------|---------------------------------------|-------------------------------------|--------|
| settings_bp   | /settings  | `/settings`                           | GET       | 显示系统设置页面                      | system_general.html                 | ★★★★★  |
| settings_bp   | /settings  | `/settings`                           | POST      | 保存全部系统设置                      | （同上，重定向或渲染）              | ★★★★★  |
| users_bp      | /users     | `/users`                              | GET       | 用户列表（搜索、分页）                | system_userslist.html               | ★★★★★  |
| users_bp      | /users     | `/users/new`                          | GET/POST  | 新建用户（实际复用 edit 模板）        | system_useredit.html                | ★★★★☆  |
| users_bp      | /users     | `/users/<int:id>/edit`                | GET/POST  | 编辑用户（id > 0）                    | system_useredit.html                | ★★★★☆  |
| users_bp      | /users     | `/users/<int:id>/toggle-active`       | POST      | 切换启用/禁用状态                     | （JSON 或重定向）                   | ★★★★☆  |

## 2. 左侧导航（稳定高亮规则）

建议抽取为可复用片段：`templates/partials/_admin_sidebar.html` 或 `templates/system/_sidebar.html`

```jinja
<nav class="admin-sidebar">
  <ul class="nav flex-column">
    <li class="nav-item">
      <a class="nav-link {% if request.path.startswith('/settings') %}active{% endif %}"
         href="{{ url_for('settings.index') }}">
        <i class="bi bi-gear"></i> 系统设置
      </a>
    </li>
    <li class="nav-item">
      <a class="nav-link {% if request.path.startswith('/users') %}active{% endif %}"
         href="{{ url_for('users.index') }}">
        <i class="bi bi-people"></i> 用户管理
      </a>
    </li>
  </ul>
</nav>
```

## 3. 系统设置 - 单页详细设计

**页面**：`/settings`  
**模板**：`templates/system_general.html`

**布局风格**：卡片分组 + 垂直表单 + 底部统一保存按钮（参考现有个人设置页面风格）

### 卡片分组与字段清单

| 卡片标题           | Config key                          | 显示名称             | 控件类型              | 校验规则                          | 默认值示例              | 备注 |
|--------------------|-------------------------------------|----------------------|-----------------------|-----------------------------------|-------------------------|------|
| 系统基本信息       | `system_name`                       | 系统名称             | 文本输入              | 必填，3–64字符                    | FFE 项目跟进系统        | — |
|                    | `maintenance_mode`                  | 维护模式             | 开关（checkbox）      | —                                 | false                   | — |
| 国际化与时区       | `default_language`                  | 默认语言             | 下拉单选              | 必选（zh_CN / en_US）             | zh_CN                   | — |
|                    | `system_timezone`                   | 系统时区             | 下拉单选              | 必选                              | Asia/Shanghai           | — |
| 文件上传限制       | `upload_allowed_extensions`         | 允许的文件类型       | 文本（逗号分隔）      | 必填，转小写存储                  | .pdf,.jpg,.png,.xlsx    | — |
|                    | `upload_max_size_mb`                | 单文件最大大小(MB)   | 数字输入 / 下拉       | 必填，1–200                       | 10                      | — |
| 安全策略           | `password_min_length`               | 密码最小长度         | 数字输入 / 下拉       | 必填，6–32                        | 8                       | — |
|                    | `login_failure_lock_count`          | 登录失败锁定次数     | 数字输入              | 0–20（0=不锁定）                  | 5                       | — |
|                    | `login_failure_lock_minutes`        | 锁定持续时间(分钟)   | 数字输入              | 1–1440                            | 15                      | — |

## 4. 用户管理 - 详细设计

### 4.1 用户列表

**页面**：`/users`  
**模板**：`templates/system_userslist.html`

**显示列**

| 列     | 字段来源                  | 显示形式                     | 可排序 | 可搜索 | 备注 |
|--------|---------------------------|------------------------------|--------|--------|------|
| ID     | id                        | 数字                         | 是     | 否     | — |
| 用户名 | username                  | 链接 → 编辑页                | 是     | 是     | — |
| 角色   | is_admin                  | 徽章：管理员 / 普通用户      | 是     | 否     | — |
| 状态   | is_active + locked_until  | 启用 / 禁用 / 锁定至…        | 是     | 是     | — |
| 操作   | —                         | 编辑 + 启用/禁用按钮         | —      | —      | — |

### 4.2 新建/编辑页面

**页面**：`/users/new` 与 `/users/<int:id>/edit`  
**模板**：`templates/system_useredit.html`（共用）

**动态标题**：

- 新建：创建新用户
- 编辑：编辑用户 - {{ user.username }}

**表单字段**

| 字段名                  | 控件类型           | 新建默认值      | 编辑时行为                     | 校验规则                     | 备注 |
|-------------------------|--------------------|-----------------|--------------------------------|------------------------------|------|
| username                | 文本输入           | —               | 显示但禁用（建议不允许修改）   | 必填，唯一，3–64字符         | — |
| nickname                | 文本输入           | —               | 可编辑                         | 可选，最大64字符             | — |
| email                   | 邮箱输入           | —               | 可编辑                         | 可选，邮箱格式               | — |
| password                | 密码输入           | 必填            | 留空=不修改                    | 新建必填，编辑可选           | — |
| password_confirm        | 密码输入（确认）   | —               | 同上                           | 与 password 一致             | — |
| is_admin                | checkbox           | false           | 可编辑                         | —                            | — |
| is_active               | checkbox           | true            | 可编辑                         | —                            | — |
| theme                   | 下拉单选           | light / auto    | 可编辑                         | —                            | — |
| notifications_enabled   | checkbox           | true            | 可编辑                         | —                            | — |
| preferred_language      | 下拉单选           | zh_CN           | 可编辑                         | —                            | — |

**账户状态区域**（仅编辑模式）

- 当前状态显示
- 切换按钮：禁用账户 / 启用账户

## 5. 模板文件汇总（统一前缀 system_）

| 功能               | 模板路径                            | 说明                     |
|--------------------|-------------------------------------|--------------------------|
| 系统设置单页       | templates/system_general.html       | 所有配置在一个页面       |
| 用户列表           | templates/system_userslist.html     | 表格 + 搜索 + 分页       |
| 用户新建/编辑      | templates/system_useredit.html      | 条件判断新建或编辑模式   |
| 左侧导航片段       | templates/partials/_admin_sidebar.html 或 templates/system/_sidebar.html | 可复用                   |
| 布局继承模板       | templates/system_layout.html        | （建议）统一管理后台布局 |

## 6. 优先级与里程碑（建议顺序）

1. Config 表创建 + settings_bp + system_general.html 框架与读写逻辑
2. users_bp + system_userslist.html（列表展示）
3. system_useredit.html（新建 + 编辑基本字段 + 密码处理）
4. 启用/禁用功能（toggle-active 路由 + 按钮交互）
5. 左侧导航 + 管理员权限保护
6. flash 提示、表单校验、错误处理、维护模式简单实现

如果这份更新后的策划书符合你的预期，请直接告诉我下一步指令，例如：

- “可以开始写 settings_bp 和 system_general.html 的代码骨架”
- “先写 users_bp 的路由和 system_userslist.html”
- “还需要修改/补充的内容是……”

等待你的确认。
