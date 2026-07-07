# 代码快照

> 生成日期：2026-07-06  
> 用途：避免每次 session 全库扫描，减少 token 消耗

---

## 一、模型清单

### 1.1 core/models.py

| 模型 | 字段 | 类型 | 参数 |
|------|------|------|------|
| BaseModel | created_at | DateTimeField | auto_now_add=True |
| BaseModel | updated_at | DateTimeField | auto_now=True |
| User(AbstractUser) | nickname | CharField | max_length=64, null=True, blank=True |
| User(AbstractUser) | email | EmailField | null=True, blank=True, db_index=True |
| User(AbstractUser) | is_active | BooleanField | default=True, db_index=True |
| User(AbstractUser) | is_admin | BooleanField | default=False |
| User(AbstractUser) | role | CharField | max_length=20, choices, default=employee, db_index=True |
| User(AbstractUser) | permissions | JSONField | default=list |
| User(AbstractUser) | failed_login_attempts | IntegerField | default=0 |
| User(AbstractUser) | locked_until | DateTimeField | null=True, blank=True |
| User(AbstractUser) | theme | CharField | max_length=20, choices, default=default |
| User(AbstractUser) | notifications_enabled | BooleanField | default=True |
| User(AbstractUser) | preferred_language | CharField | max_length=10, default=zh |
| User(AbstractUser) | navigation_cards | JSONField | default=list, blank=True |
| User(AbstractUser) | last_login_at | DateTimeField | null=True, blank=True |
| SystemSetting | key | CharField | max_length=128, unique=True, db_index=True |
| SystemSetting | value | TextField | |
| SystemSetting | description | CharField | max_length=255, null=True, blank=True |
| SystemSetting | updated_at | DateTimeField | auto_now=True |
| Taxonomy | name | CharField | max_length=128 |
| Taxonomy | slug | CharField | max_length=128, unique=True, db_index=True |
| Taxonomy | description | CharField | max_length=512, null=True, blank=True |
| TaxonomyItem | taxonomy | ForeignKey | Taxonomy, CASCADE, related_name=items |
| TaxonomyItem | name | CharField | max_length=256 |
| TaxonomyItem | description | CharField | max_length=512, null=True, blank=True |
| TaxonomyItem | weight | IntegerField | default=0 |
| ChinaRegion | code | CharField | max_length=6, unique=True |
| ChinaRegion | name | CharField | max_length=100 |
| ChinaRegion | level | IntegerField | choices, db_index=True |
| ChinaRegion | parent | ForeignKey | self, CASCADE, null=True, blank=True |

### 1.2 core/node/models.py

| 模型 | 字段 | 类型 | 参数 |
|------|------|------|------|
| NodeType | name | CharField | max_length=100 |
| NodeType | slug | CharField | max_length=50, unique=True, db_index=True |
| NodeType | description | CharField | max_length=500, null=True, blank=True |
| NodeType | icon | CharField | max_length=50, default=bi-folder |
| NodeType | author | CharField | max_length=100, null=True, blank=True |
| NodeType | fields_config | JSONField | default=list |
| NodeType | is_active | BooleanField | default=True |
| Node | node_type | ForeignKey | NodeType, CASCADE |
| Node | created_by | ForeignKey | User, SET_NULL, null=True |
| Node | updated_by | ForeignKey | User, SET_NULL, null=True |

### 1.3 core/module/models.py

| 模型 | 字段 | 类型 | 参数 |
|------|------|------|------|
| Module | module_id | CharField | max_length=50, unique=True |
| Module | name | CharField | max_length=100 |
| Module | version | CharField | max_length=20 |
| Module | author | CharField | max_length=100, null=True, blank=True |
| Module | description | TextField | null=True, blank=True |
| Module | icon | CharField | max_length=50, default=bi-wrench |
| Module | path | CharField | max_length=200 |
| Module | is_installed | BooleanField | default=False |
| Module | is_active | BooleanField | default=False |
| Module | is_system | BooleanField | default=False |
| Module | module_type | CharField | max_length=20, choices |
| Module | install_on_init | BooleanField | default=True |
| Module | installed_at | DateTimeField | null=True, blank=True |
| Module | activated_at | DateTimeField | null=True, blank=True |
| ToolType | name | CharField | max_length=100 |
| ToolType | slug | CharField | max_length=50, unique=True, db_index=True |
| ToolType | description | CharField | max_length=500, null=True, blank=True |
| ToolType | icon | CharField | max_length=50, default=bi-wrench |
| ToolType | author | CharField | max_length=100, null=True, blank=True |
| ToolType | is_active | BooleanField | default=True |

### 1.4 core/smtp/models.py

| 模型 | 字段 | 类型 | 参数 |
|------|------|------|------|
| EmailTemplate | name | CharField | max_length=64, unique=True |
| EmailTemplate | subject | CharField | max_length=255 |
| EmailTemplate | html_body | TextField | |
| EmailTemplate | text_body | TextField | blank=True |
| EmailTemplate | description | CharField | max_length=255, blank=True |
| EmailTemplate | is_active | BooleanField | default=True |
| EmailLog | from_email | EmailField | |
| EmailLog | to_email | TextField | |
| EmailLog | subject | CharField | max_length=255 |
| EmailLog | text_body | TextField | blank=True, default="" |
| EmailLog | html_body | TextField | blank=True, default="" |
| EmailLog | template_name | CharField | max_length=64, blank=True |
| EmailLog | status | CharField | max_length=16, choices, default=pending, db_index=True |
| EmailLog | error_message | TextField | blank=True, default="" |
| EmailLog | retry_count | IntegerField | default=0 |
| EmailLog | sent_at | DateTimeField | null=True, blank=True |

### 1.5 modules/customer/models.py

| 模型 | 字段 | 类型 | 参数 |
|------|------|------|------|
| CustomerFields | node | OneToOneField | Node, CASCADE |
| CustomerFields | customer_name | CharField | max_length=200, unique=True |
| CustomerFields | customer_code | CharField | max_length=50, unique=True, null=True, blank=True |
| CustomerFields | customer_type | ForeignKey | TaxonomyItem, SET_NULL, null=True |
| CustomerFields | enterprise_name | CharField | max_length=200, null=True, blank=True |
| CustomerFields | phone1 | CharField | max_length=50, null=True, blank=True |
| CustomerFields | email1 | EmailField | null=True, blank=True |
| CustomerFields | phone2 | CharField | max_length=50, null=True, blank=True |
| CustomerFields | email2 | EmailField | null=True, blank=True |
| CustomerFields | linkedin | URLField | max_length=200, null=True, blank=True |
| CustomerFields | country | ForeignKey | TaxonomyItem, SET_NULL, null=True |
| CustomerFields | province | CharField | max_length=50, null=True, blank=True |
| CustomerFields | address | CharField | max_length=200, null=True, blank=True |
| CustomerFields | postal_code | CharField | max_length=10, null=True, blank=True |
| CustomerFields | industry | CharField | max_length=50, null=True, blank=True |
| CustomerFields | enterprise_type | ForeignKey | TaxonomyItem, SET_NULL, null=True |
| CustomerFields | registered_capital | DecimalField | max_digits=15, decimal_places=2, null=True, blank=True |
| CustomerFields | customer_level | ForeignKey | TaxonomyItem, SET_NULL, null=True |
| CustomerFields | credit_limit | DecimalField | max_digits=15, decimal_places=2, null=True, blank=True |
| CustomerFields | website | URLField | max_length=200, null=True, blank=True |
| CustomerFields | notes | TextField | null=True, blank=True |
| CustomerFields | has_whatsapp | BooleanField | null=True, blank=True, default=None |

### 1.6 modules/clock/models.py

| 模型 | 字段 | 类型 | 参数 |
|------|------|------|------|
| ClockModel | (无业务字段) | - | 占位模型，仅注册数据库表 |

---

## 二、服务层签名

### 2.1 AuthService (BaseService)
| 方法 | 返回 | 说明 |
|------|------|------|
| authenticate(username, password) | User \| None | 认证用户 |
| login(_request, username, password) | dict | 登录并返回结果 |
| is_account_locked(user) | bool | 检查账号是否锁定 |
| unlock_expired_accounts() | int | 解锁过期账号 |
| get_login_max_failures() | int | 获取最大失败次数 |
| get_login_lock_minutes() | int | 获取锁定分钟数 |

### 2.2 BaseService
| 方法 | 返回 | 说明 |
|------|------|------|
| get_by_id(entity_id) | Any \| None | 按ID获取 |
| get_by_slug(slug) | Any \| None | 按slug获取 |
| get_list(**filters) | QuerySet | 获取列表 |
| create(**kwargs) | Model | 创建记录 |
| update(entity_id, **kwargs) | (Model, bool) | 更新记录 |
| delete(entity_id) | bool | 删除记录 |
| get_or_raise(entity_id, error_msg) | Any | 获取或抛异常 |
| get_first(**filters) | Any \| None | 按条件获取第一条 |
| get_or_none(**filters) | Any \| None | 按条件获取或None |

### 2.3 ChinaRegionService
| 方法 | 返回 | 说明 |
|------|------|------|
| import_from_file(file_path) | dict | 从文件导入省市区 |
| import_from_url(url) | dict | 从URL下载省市区数据 |
| get_provinces() | list | 获取所有省份 |
| get_cities(province_code) | list | 获取城市列表 |
| get_districts(city_code) | list | 获取区县列表 |
| get_by_code(code) | ChinaRegion \| None | 按代码获取 |
| search(keyword, limit=20) | list | 搜索 |
| get_full_path(region_code) | str | 获取完整路径 |
| get_tree() | list[dict] | 获取树形结构（1次查询） |
| get_stats() | dict | 获取统计 |
| download_to_file(url) | dict | 下载数据到文件 |

### 2.4 CronService (SingletonMixin)
| 方法 | 返回 | 说明 |
|------|------|------|
| register(task) | - | 注册任务 |
| unregister(task_name) | - | 注销任务 |
| start() | - | 启动 |
| stop() | - | 停止 |
| get_status() | dict | 获取状态 |
| trigger(task_name) | dict | 触发任务 |
| toggle(task_name, enabled) | dict | 启用/禁用 |

### 2.5 LogService
| 方法 | 返回 | 说明 |
|------|------|------|
| get_client_ip(request) | str | 获取客户端IP |
| log_login_attempt(request, username, success, reason) | - | 记录登录尝试 |
| log_logout(_user, username, ip) | - | 记录登出 |
| log_permission_denied(request, user, resource, reason) | - | 记录权限拒绝 |
| log_security_event(event_type, details, level) | - | 记录安全事件 |
| log_api_access(request, endpoint, user) | - | 记录API访问 |
| log_data_export(request, user, export_type, record_count) | - | 记录数据导出 |
| log_failed_validation(request, form_name, errors) | - | 记录验证失败 |
| get_log_files() | list[dict] | 获取日志文件列表 |
| read_log(log_type, page, page_size, level) | dict | 读取日志 |
| get_log_stats(log_type) | dict | 获取日志统计 |

### 2.6 PermissionService
| 方法 | 返回 | 说明 |
|------|------|------|
| get_all_permissions() | list[tuple] | 获取所有权限 |
| get_system_permissions() | dict | 获取系统权限 |
| get_role_permissions(role) | list[str] | 获取角色权限 |
| save_role_permissions(role, permissions) | - | 保存角色权限 |
| has_permission(user, permission) | bool | 检查权限 |
| get_user_effective_permissions(user) | list[str] | 获取用户有效权限 |
| can_access_admin(user) | bool | 检查管理员访问 |
| init_default_role_permissions() | - | 初始化默认角色权限 |
| get_node_permissions() | dict | 获取节点权限 |

### 2.7 SettingsService (CachedServiceMixin)
| 方法 | 返回 | 说明 |
|------|------|------|
| get_all_settings(as_dict=True) | dict | 获取所有设置 |
| get_setting(key, default=None, parse_json=False) | Any | 获取设置值 |
| save_setting(key, value, description) | SystemSetting | 保存设置 |
| save_settings_bulk(settings_dict) | int | 批量保存 |
| reset_to_default(key) | int | 重置为默认 |
| clear_cache() | - | 清除缓存 |

### 2.8 TaxonomyService (BaseService)
| 方法 | 返回 | 说明 |
|------|------|------|
| get_all_taxonomies() | QuerySet | 所有词汇表 |
| get_taxonomy_list(search) | QuerySet | 搜索词汇表 |
| check_slug_exists(slug) | bool | 检查slug是否存在 |
| check_slug_exists_exclude(slug, exclude_id) | bool | 检查slug排除ID |
| get_taxonomy_by_id(id) | Taxonomy \| None | 按ID获取 |
| get_taxonomy_by_slug(slug) | Taxonomy \| None | 按slug获取 |
| create_taxonomy(name, slug, description) | Taxonomy | 创建词汇表 |
| update_taxonomy(id, name, slug, description) | Taxonomy | 更新词汇表 |
| delete_taxonomy(id) | bool | 删除词汇表 |
| get_items(taxonomy_id) | list | 获取词汇项列表 |
| get_item_by_id(item_id) | TaxonomyItem \| None | 按ID获取词汇项 |
| create_item(taxonomy_id, name, description, weight) | TaxonomyItem | 创建词汇项 |
| update_item(item_id, name, description, weight) | TaxonomyItem | 更新词汇项 |
| delete_item(item_id) | bool | 删除词汇项 |
| reorder_items(taxonomy_id, item_ids) | bool | 重排词汇项 |
| init_default_taxonomies() | int | 初始化默认词汇表 |

### 2.9 TimeService
| 方法 | 返回 | 说明 |
|------|------|------|
| is_sync_enabled() | bool | 时间同步是否启用 |
| get_current_time() | str | 获取当前时间字符串 |
| get_current_datetime() | datetime | 获取当前datetime |
| get_timezone() | str | 获取时区 |
| get_sync_status() | dict | 获取同步状态 |

### 2.10 TimeSyncService (SingletonMixin)
| 方法 | 返回 | 说明 |
|------|------|------|
| is_enabled() | bool | 是否启用 |
| get_sync_interval() | int | 获取同步间隔 |
| sync_time() | bool | 同步时间 |
| get_current_time() | datetime | 获取当前时间 |
| get_current_time_str(fmt) | str | 获取时间字符串 |
| get_status() | dict | 获取状态 |

### 2.11 UserService (BaseService)
| 方法 | 返回 | 说明 |
|------|------|------|
| get_user_by_id(user_id) | User \| None | 按ID获取 |
| get_user_by_username(username) | User \| None | 按用户名获取 |
| get_user_list(search_term, only_active, exclude_admin, role) | list | 获取用户列表 |
| create_user(username, nickname, email, password, role, is_admin) | User | 创建用户 |
| update_user(user_id, username, nickname, email, password, role, is_admin, is_active) | User | 更新用户 |
| toggle_user_active(user_id, active) | User | 切换激活状态 |
| get_user_stats() | dict | 获取用户统计 |
| update_profile(user_id, nickname, email) | User | 更新个人信息 |
| update_preferences(user_id, theme, notifications_enabled, preferred_language) | User | 更新偏好 |
| change_password(user_id, new_password) | User | 修改密码 |
| get_navigation_cards(user_id) | list | 获取导航卡片 |
| save_navigation_cards(user_id, cards) | User | 保存导航卡片 |

### 2.12 ModuleService
| 方法 | 返回 | 说明 |
|------|------|------|
| scan_modules() | list[dict] | 扫描模块目录 |
| scan_register_install(do_install, dry_run, respect_install_on_init) | dict | 扫描+注册+安装 |
| scan_and_register_modules() | list[Module] | 扫描+注册 |
| load_module_info(module_dir) | dict \| None | 加载模块信息 |
| register_module(module_info) | Module | 注册模块 |
| install_module(module_id) | tuple | 安装模块 |
| register_and_install(module_info) | Module | 注册+安装 |
| get_frontpage_modules() | list[dict] | 获取首页卡片模块 |
| create_module_taxonomies(module) | int | 创建模块词汇表 |
| check_dependencies(module_id, visited) | tuple | 检查依赖 |
| verify_dependencies(module_id) | tuple | 验证依赖 |
| get_dependency_chain(module_id) | list | 获取依赖链 |
| enable_module(module_id) | Module \| None | 启用模块 |
| disable_module(module_id) | Module \| None | 禁用模块 |
| get_all() / get_installed() / get_active() | list | 模块列表 |
| get_by_id(module_id) | Module \| None | 按ID获取 |
| sync_node_type / sync_tool_type(module) | NodeType/ToolType | 同步类型 |
| create_module(...) | dict | 创建新模块 |

### 2.13 NodeTypeService
| 方法 | 返回 | 说明 |
|------|------|------|
| get_all() / get_all_including_inactive() | list | 获取节点类型 |
| get_by_id / get_by_slug(id/slug) | NodeType \| None | 获取 |
| get_by_id_or_404 / get_by_slug_or_404(id/slug) | NodeType | 获取或404 |
| create(data) | NodeType | 创建 |
| update(id, data) | NodeType \| None | 更新 |
| delete(id) | bool | 删除 |
| enable / disable / toggle_active(id) | bool | 状态切换 |
| get_node_count(id) | int | 获取节点计数 |
| init_default_node_types() | - | 初始化 |

### 2.14 NodeService
| 方法 | 返回 | 说明 |
|------|------|------|
| get_nodes(node_type_slug) | list | 获取节点列表 |
| get_node(slug, node_id) | Node \| None | 获取节点 |
| get_by_id(node_id) | Node \| None | 按ID获取 |
| create_node(slug, data, user) | Node \| None | 创建节点 |
| update_node(node_id, data) | Node \| None | 更新节点 |
| delete_node(node_id) | bool | 删除节点 |
| get_list(slug, search) | list | 获取列表 |

### 2.15 SmtpService
| 方法 | 返回 | 说明 |
|------|------|------|
| get_provider_presets(provider) | dict | 获取服务商预设 |
| get_current_config() | dict | 获取当前配置 |
| save_config(config) | - | 保存配置 |
| test_connection(config) | (bool, str) | 测试连接 |
| update_django_settings() | - | 更新Django设置 |

### 2.16 EmailService
| 方法 | 返回 | 说明 |
|------|------|------|
| send_email(to, subject, body, html_body, from_email, async_send) | bool \| int | 发送邮件 |
| send_template_email(to, template_name, context, async_send) | bool \| int | 发送模板邮件 |
| process_pending_emails() | int | 处理待发送 |
| cleanup_old_logs() | int | 清理旧日志 |
| send_verification_code(to, code, expire_minutes, request, async_send) | bool \| int | 发送验证码 |
| send_password_reset(to, reset_link, expire_hours, request, async_send) | bool \| int | 发送密码重置 |
| send_notification(to, title, message, action_url, action_text, request, async_send) | bool \| int | 发送通知 |

### 2.17 TemplateService (SMTP)
| 方法 | 返回 | 说明 |
|------|------|------|
| get_template(name) | EmailTemplate \| None | 获取模板 |
| render_subject(template, context) | str | 渲染主题 |
| render_body(template, context) | (str, str) | 渲染正文 |
| list_templates() | list | 模板列表 |
| create_template(name, subject, html_body, text_body, description) | EmailTemplate | 创建模板 |
| update_template(...) | EmailTemplate | 更新模板 |
| delete_template(template) | - | 删除模板 |
| init_default_templates() | int | 初始化默认模板 |

### 2.18 CustomerService
| 方法 | 返回 | 说明 |
|------|------|------|
| get_list(search, customer_type_id, customer_level_id, user) | list | 获取客户列表 |
| get_by_id(customer_id) | CustomerFields \| None | 按ID获取 |
| create(user, data) | CustomerFields | 创建客户 |
| update(customer_id, _user, data) | CustomerFields \| None | 更新客户 |
| delete(customer_id) | bool | 删除客户 |
| get_count() / get_recent_count(days) | int | 计数统计 |
| init_sample_data() | int | 初始化样本数据 |

---

## 三、已知遗留问题

| # | 优先级 | 描述 | 来源 |
|---|--------|------|------|
| 1 | LOW | 24 处 CharField/TextField/EmailField 的 `null=True` → `blank=True` 评估 | 第二批次计划 #23-46 |
| 2 | INFO | `logs_api` 视图已定义但未注册路由（预留） | `core/views/logs.py:55` |
| 3 | INFO | ~90 处 PLC0415 noqa（延迟导入，避免循环依赖，有意为之） | 全局 |
| 4 | INFO | ~25 处 ARG001 noqa（视图参数由 Django 分发器传入，有意为之） | 全局 |

---

## 四、统计汇总

| 类别 | 数量 |
|------|------|
| 模型（含抽象类） | 15 |
| 实体模型 | 14 |
| 服务类 | 30 |
| 公共方法 | ~200 |
| 已知遗留问题 | 4 |
