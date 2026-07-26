# core/services 服务层规范

> 文档版本：2.5  
> 创建日期：2026-04-07  
> 最后更新：2026-07-22

---

## 一、概述

### 1.1 模块定位

服务层（Services）是 core 模块的业务逻辑核心，封装所有与数据库操作相关的业务规则，为视图层提供清晰的数据访问接口。

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **单一职责** | 每个服务类只负责一个业务领域 |
| **数据封装** | 视图层不应直接操作 Model，通过服务层访问 |
| **事务边界** | 复杂业务操作在服务层处理事务 |
| **返回类型** | 方法返回模型实例或字典，避免直接暴露 QuerySet |

### 1.3 服务列表

| 文件 | 服务类 | 用途 |
|------|--------|------|
| `auth_service.py` | AuthService | 用户认证、登录、锁定 |
| `permission_service.py` | PermissionService | 权限定义、角色管理、权限检查 |
| `user_service.py` | UserService | 用户 CRUD、个人偏好 |
| `settings_service.py` | SettingsService | 系统配置管理 |
| `taxonomy_service.py` | TaxonomyService | 词汇表和词汇项管理 |
| `watermark_service.py` | WatermarkService | 图片水印处理 |
| `china_region_service.py` | ChinaRegionService | 中国行政区划查询 |
| `cron_service.py` | CronService | 定时任务调度 |
| `time_service.py` | TimeService | 时间工具服务 |
| `time_sync_service.py` | TimeSyncService | 时间同步服务 |
| `log_service.py` | LogService | 日志记录、审计追踪 |
| `version_service.py` | VersionService | 版本信息管理 |
| `sample_data_service.py` | SampleDataService | 示例数据生成 |
| `base_service.py` | BaseService | 服务基类（抽象基类，不直接导出） |
|  |  |  |
| **任务（core/services/tasks/）** |  |  |
| `base.py` | CronTask | 定时任务基类 |
| `time_sync_task.py` | TimeSyncTask | 时间同步任务 |
| `cache_cleanup_task.py` | CacheCleanupTask | 缓存清理任务 |
| `email_sending_task.py` | EmailSendingTask | 定时邮件发送任务 |
| `email_cleanup_task.py` | EmailCleanupTask | 定时邮件日志清理任务 |
|  |  |  |
| **节点服务（core/node/services/）** |  |  |
| `node_service.py` | NodeService | 节点 CRUD 操作 |
| `node_type_service.py` | NodeTypeService | 节点类型管理 |
|  |  |  |
| **SMTP 服务（core/smtp/services/）** |  |  |
| `smtp_service.py` | SmtpService | SMTP 配置管理、连接测试、服务商预设 |
| `email_service.py` | EmailService | 邮件发送、发送历史、日志清理 |
| `template_service.py` | TemplateService | 邮件模板管理 |
|  |  |  |
| **模块管理服务（core/module/services/）** |  |  |
| `module_service.py` | ModuleService | 模块安装/卸载/依赖管理 |
|  |  |  |
| **模块服务（modules/）** |  |  |
| `modules/customer/services.py` | CustomerService | 海外客户管理服务 |
| `modules/clock/services.py` | ClockService | 时钟服务 |

---

## 二、AuthService - 认证服务

### 2.1 用途
处理用户登录、登出、账号锁定等认证逻辑

### 2.2 方法说明

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `authenticate()` | username, password | `User \| None` | 验证用户凭据 |
| `login()` | username, password | `Dict` | 处理登录，返回 success/message/user |
| `is_account_locked()` | user | `bool` | 检查账号是否锁定 |
| `unlock_expired_accounts()` | - | `int` | 解锁所有过期锁定账号 |
| `get_login_max_failures()` | - | `int` | 获取登录失败最大次数（默认5） |
| `get_login_lock_minutes()` | - | `int` | 获取锁定时间（默认30分钟） |

### 2.3 业务流程

```
用户登录 → 验证用户名存在 → 检查锁定状态 → 检查激活状态 
→ 验证密码 → 记录成功/失败 → 返回结果
```

---

## 三、PermissionService - 权限服务

### 3.1 用途
定义权限列表、角色默认权限、权限检查

### 3.2 核心常量

```python
from core.constants import UserRole

# 权限定义
PERMISSIONS = [
    ('system.settings.view', '系统设置 - 查看'),
    ('system.settings.modify', '系统设置 - 修改'),
    ('permissions.view', '权限管理 - 查看'),
    ('permissions.modify', '权限管理 - 修改'),
    ('user.create', '人员管理 - 创建'),
    ('user.read', '人员管理 - 查看'),
    ('user.update', '人员管理 - 修改'),
    ('user.delete', '人员管理 - 删除'),
    ('importexport.view', '数据导入导出 - 访问'),
]

# 角色默认权限
ROLE_DEFAULT_PERMISSIONS = {
    UserRole.MANAGER: ['importexport.view'],
    UserRole.LEADER: ['importexport.view'],
    UserRole.EMPLOYEE: [],
}
```

### 3.3 方法说明

| 方法 | 说明 |
|------|------|
| `get_all_permissions()` | 获取所有可用权限列表 |
| `get_system_permissions()` | 获取按模块分组的系统权限 |
| `get_role_permissions()` | 获取指定角色的默认权限 |
| `get_role_permissions_from_db()` | 从数据库获取角色权限（优先）或默认值 |
| `save_role_permissions()` | 保存角色权限到数据库 |
| `has_permission()` | 检查用户是否拥有指定权限 |
| `get_user_effective_permissions()` | 获取用户有效权限列表 |
| `can_access_admin()` | 检查是否可以访问后台（admin） |
| `init_default_role_permissions()` | 初始化角色默认权限到数据库 |
| `check_node_permission()` | user, node, permission_type | `tuple[bool, str \| None]` | 检查用户对指定节点的操作权限 |
| `get_node_permissions()` | - | `dict` | 获取节点权限（从模块配置动态读取） |

---

## 四、UserService - 用户服务

### 4.1 用途
封装用户相关的所有数据库操作和业务规则

### 4.2 方法说明

| 方法 | 说明 |
|------|------|
| `get_user_by_id()` | 根据 ID 获取用户（排除 ID=1 系统管理员） |
| `get_user_by_username()` | 通过用户名查找用户 |
| `get_user_list()` | 获取用户列表（支持搜索、过滤、排序） |
| `create_user()` | 新建用户（含密码强度验证） |
| `update_user()` | 更新用户信息（严格保护 ID=1） |
| `toggle_user_active()` | 切换启用/禁用状态（保护 ID=1） |
| `get_user_stats()` | 获取用户统计数据 |
| `update_profile()` | 更新个人资料（昵称、邮箱） |
| `update_preferences()` | 更新偏好设置（主题、通知、语言） |
| `change_password()` | 修改用户密码 |
| `get_navigation_cards()` | 获取导航卡片（按 position 排序） |
| `save_navigation_cards()` | 保存导航卡片（最多12个） |
| `assign_position()` | 为新卡片分配空 position |

---

## 五、SettingsService - 系统设置服务

### 5.1 用途
系统配置管理，提供读取/保存/缓存/类型转换功能

### 5.2 默认配置

SettingsService 共定义 **57** 项默认配置：

| 分类 | 配置项 | 默认值 |
|------|--------|--------|
| 系统 | system_name | 仙芙CIMF |
| 欢迎 | welcome_title | 欢迎！ |
| 欢迎 | welcome_subtitle | 让我们一起把项目完善吧。 |
| 欢迎 | welcome_intro | 初始用户名：admin 初始密码：admin123 |
| 图标 | site_logo_enabled | true |
| 图标 | site_logo_path | （空） |
| 上传 | upload_max_size_mb | 12 |
| 上传 | upload_max_files | 20 |
| 上传 | upload_allowed_extensions | pdf,doc,docx,xls,xlsx,jpg,png,jpeg,zip,rar |
| 会话 | session_timeout_minutes | 30 |
| 登录 | login_max_failures | 5 |
| 登录 | login_lock_minutes | 30 |
| 审计 | enable_audit_log | true |
| 审计 | log_retention_days | 90 |
| 水印 | enable_web_watermark | false |
| 水印 | web_watermark_content | username,system_name,datetime |
| 水印 | web_watermark_custom_text | 自定义文字 |
| 水印 | web_watermark_opacity | 0.15 |
| 水印 | enable_watermark_console_detection | false |
| 水印 | enable_watermark_shortcut_block | false |
| 水印 | enable_export_watermark | false |
| 时间 | enable_time_sync | true |
| 时间 | time_server_url | https://api.uuni.cn/api/time |
| 时间 | time_zone | Asia/Shanghai |
| 时间 | time_sync_interval | 15 |
| 时间 | time_sync_max_retries | 5 |
| 时间 | system_synced_time | （空） |
| 时间 | system_sync_monotonic | 0 |
| 定时任务 | cron_time_sync_enabled | true |
| 定时任务 | cron_cache_cleanup_enabled | true |
| 定时任务 | cron_email_sending_enabled | false |
| 定时任务 | cron_email_cleanup_enabled | false |
| 定时任务 | cron_email_cleanup_interval | 86400 |
| 维护 | maintenance_mode | false |
| 维护 | allow_registration | false |
| SMTP | smtp_enabled | false |
| SMTP | smtp_provider | gmail_tls |
| SMTP | smtp_host | smtp.gmail.com |
| SMTP | smtp_port | 587 |
| SMTP | smtp_use_ssl | false |
| SMTP | smtp_use_tls | true |
| SMTP | smtp_username | （空） |
| SMTP | smtp_from_email | （空） |
| SMTP | smtp_from_name | 仙芙CIMF |
| SMTP | smtp_timeout | 30 |
| SMTP | smtp_skip_verify | false |
| SMTP | smtp_batch_size | 10 |
| SMTP | smtp_password | （空） |
| SMTP | smtp_retry_count | 3 |
| SMTP | smtp_log_days | 30 |
| SMTP | smtp_failed_notify | false |
| SMTP | smtp_notify_email | （空） |
| SMTP | smtp_system_url | （空） |
| SMTP | smtp_proxy_host | 127.0.0.1 |
| SMTP | smtp_proxy_port | 10808 |
| SMTP | smtp_use_proxy | false |
| SMTP | smtp_send_interval | 240 |

### 5.3 方法说明

| 方法 | 说明 |
|------|------|
| `get_all_settings()` | 获取所有系统设置（带缓存） |
| `get_setting()` | 获取单个设置（支持默认值） |
| `save_setting()` | 保存单个设置（自动清除缓存） |
| `save_settings_bulk()` | 批量保存设置 |
| `reset_to_default()` | 重置为默认值 |
| `clear_cache()` | 清除缓存 |

### 5.4 类型转换

数据库存储字符串，自动转换为：
- `true/false` → `bool`
- 纯数字（无小数点） → `int`
- 纯数字（有小数点） → `float`
- 其他 → `str`

---

## 六、TaxonomyService - 词汇表服务

### 6.1 用途
词汇表和词汇项的 CRUD 操作，以及预置数据初始化

### 6.2 预置词汇表

系统预置 **47 个**词汇表，包括：

| 类别 | 数量 | 示例 |
|------|------|------|
| 旧版移植 | 18 | 性别、客户类型、国家/地区、项目状态、部门 |
| 新增业务 | 9 | 开发技术、客户等级、建筑类型、会员等级 |
| 经济普查 | 10 | 经济类型、企业性质、经营状态、从业人员规模 |

### 6.3 方法说明

| 方法 | 说明 |
|------|------|
| `get_all_taxonomies()` | 获取所有词汇表 |
| `get_taxonomy_list(search)` | 获取词汇表列表，支持搜索 |
| `check_slug_exists(slug)` | 检查词汇表标识是否已存在 |
| `check_slug_exists_exclude(slug, exclude_id)` | 检查词汇表标识是否已存在（排除指定 ID） |
| `get_taxonomy_by_id(taxonomy_id)` | 获取词汇表详情 |
| `get_taxonomy_by_slug(slug)` | 通过 slug 获取词汇表 |
| `create_taxonomy(name, slug, description)` | 创建词汇表 |
| `update_taxonomy(taxonomy_id, name, slug, description)` | 更新词汇表 |
| `delete_taxonomy(taxonomy_id)` | 删除词汇表（级联删除词汇项） |
| `get_items(taxonomy_id)` | 获取词汇表的所有词汇项 |
| `get_items_bulk(slugs)` | 批量获取多个词汇表的词汇项 |
| `get_item_by_id(item_id)` | 根据 ID 获取词汇项 |
| `create_item(taxonomy_id, name, description, weight)` | 创建词汇项 |
| `update_item(item_id, name, description, weight)` | 更新词汇项 |
| `delete_item(item_id)` | 删除词汇项 |
| `reorder_items(taxonomy_id, item_ids)` | 重新排序词汇项 |
| `init_default_taxonomies()` | 初始化预置分类数据 |
| `generate_items_ai(taxonomy_id, count)` | AI 生成词汇项（预留接口） |

---

## 七、WatermarkService - 水印服务

### 7.1 用途
服务端图片水印功能

### 7.2 方法说明

| 方法 | 说明 |
|------|------|
| `add_text_watermark()` | 添加文字水印 |
| `add_image_watermark()` | 添加图片水印 |

### 7.3 参数说明

| 参数 | 说明 |
|------|------|
| `position` | 位置：center, bottom_right, bottom_left, top_right, top_left |
| `opacity` | 透明度 0-1 |
| `font_size` | 字体大小 |
| `color` | RGB 颜色 |

---

## 八、ChinaRegionService - 行政区划服务

### 8.1 用途
中国省-市-县三级行政区划的数据管理和查询

### 8.2 数据来源

- 主数据源：https://raw.githubusercontent.com/modood/Administrative-divisions-of-China/master/dist/pca-code.json
- 备用镜像源：ghproxy、gitee（自动重试）
- 本地文件：`core/data/china_regions.json`
- 层级：省(1) → 市(2) → 县/区(3)

### 8.3 方法说明

| 方法 | 说明 |
|------|------|
| `import_from_file(file_path)` | 从本地 JSON 文件导入数据 |
| `import_from_url(url)` | 从网络获取并导入数据（自动重试备用源） |
| `download_to_file(url)` | 从网络下载数据保存到本地文件 |
| `get_provinces()` | 获取所有省份 |
| `get_cities()` | 获取省份下的所有城市 |
| `get_districts()` | 获取城市下的所有区县 |
| `get_by_code()` | 根据代码获取行政区划 |
| `search()` | 搜索行政区划（模糊匹配） |
| `get_full_path()` | 获取完整路径（如：广东省-深圳市-南山区） |
| `get_tree()` | 获取完整树形结构 |
| `get_stats()` | 获取统计信息 |

---

## 九、CronService - 定时任务服务

### 9.1 用途
统一的定时任务调度服务

### 9.2 设计模式
- 单例模式：确保全局只有一个调度器实例
- 后台线程：daemon 线程，不阻塞主进程

### 9.3 内置任务

| 任务 | 说明 | 默认间隔（设置值） | 类默认值 |
|------|------|----------|----------|
| TimeSyncTask | 时间同步 | 15分钟（设置值×60秒） | 900秒 |
| CacheCleanupTask | 缓存清理 | 1天（86400秒） | 3小时（10800秒） |
| EmailSendingTask | 邮件发送 | 100秒 | 100秒 |
| EmailCleanupTask | 邮件日志清理 | 1天（86400秒） | 1天（86400秒） |

### 9.4 方法说明

| 方法 | 说明 |
|------|------|
| `register()` | 注册任务 |
| `unregister()` | 注销任务 |
| `get_task()` | 获取任务实例 |
| `start()` | 启动调度器 |
| `stop()` | 停止调度器 |
| `get_status()` | 获取所有任务状态 |
| `trigger()` | 手动触发任务 |
| `toggle()` | 切换任务启用状态 |
| `set_app_ready(ready)` | 设置所有任务应用已就绪 |

---

## 十、TimeService - 时间服务

### 10.1 用途
时间工具服务，作为时间相关功能的统一入口，封装 TimeSyncService 的功能。

### 10.2 方法说明

| 方法 | 说明 |
|------|------|
| `is_sync_enabled()` | 检查时间同步是否启用 |
| `get_time_server_url()` | 获取配置的时间服务器 URL |
| `get_current_time()` | 获取当前时间字符串（格式：YYYY-MM-DD HH:MM:SS） |
| `get_current_datetime()` | 获取当前时间 datetime 对象 |
| `get_timezone()` | 获取配置的时区 |
| `get_sync_status()` | 获取时间同步状态 |

---

## 十一、TimeSyncService - 时间同步服务

### 11.1 用途
时钟同步服务，负责与远程时间服务器同步系统时间，支持多服务器和重试机制。

### 11.2 方法说明

| 方法 | 说明 |
|------|------|
| `is_enabled()` | 检查时间同步是否启用 |
| `get_sync_interval()` | 获取同步间隔（秒） |
| `get_max_retries()` | 获取最大重试次数 |
| `get_server_url()` | 获取时间服务器 URL |
| `test_connection(url)` | 测试时间服务器连接 |
| `sync_time()` | 执行时间同步 |
| `get_current_time()` | 获取当前时间 datetime 对象 |
| `get_current_time_str(fmt)` | 获取当前时间字符串 |
| `get_status()` | 获取同步状态 |

---

## 十二、LogService - 日志服务

### 12.1 用途
统一日志服务，提供日志记录（安全事件、登录、权限等）和日志读取（文件列表、分页查询、统计）功能。

### 12.2 方法说明

| 方法 | 说明 |
|------|------|
| `log_login_attempt(request, username, success, reason)` | 记录登录尝试 |
| `log_logout(user, username, ip)` | 记录登出 |
| `log_permission_denied(request, user, resource, reason)` | 记录权限拒绝 |
| `log_security_event(event_type, details)` | 记录安全事件 |
| `log_api_access(request, endpoint, user)` | 记录 API 访问 |
| `log_data_export(request, user, export_type, record_count)` | 记录数据导出 |
| `log_failed_validation(request, form_name, errors)` | 记录验证失败 |
| `get_log_files()` | 获取日志文件列表及基本信息 |
| `read_log(log_type, page, page_size, level)` | 读取日志，支持分页和级别筛选 |
| `get_log_stats(log_type)` | 获取日志统计 |

---

## 十三、服务层调用规范

### 13.1 视图层调用示例

```python
# 正确：调用服务层
def user_list(request):
    users = UserService.get_user_list(search_term='john')

# 错误：直接操作 Model
def user_list(request):
    users = User.objects.filter(username__icontains='john')
```

### 13.2 错误处理

- 服务层抛出异常，由视图层捕获处理
- 业务错误返回特定异常（如 `ValueError`, `PermissionError`）
- 数据库错误由 Django 框架处理

### 13.3 事务处理

- 简单操作：服务层方法内部处理
- 复杂操作：使用 `@transaction.atomic` 装饰器

---

---

## 十五、VersionService - 版本服务

### 15.1 用途
获取和管理系统版本信息

### 15.2 方法说明

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `get_version()` | - | str | 获取系统版本号 |
| `get_api_version()` | - | str | 获取 API 版本号 |
| `get_build_date()` | - | str | 获取构建日期 |
| `get_info()` | - | dict | 获取完整版本信息 |
| `check_compatibility()` | client_version | bool | 检查客户端版本兼容性 |
| `get_supported_versions()` | - | list | 获取支持的版本列表 |

---

## 十六、SampleDataService - 示例数据服务

### 16.1 用途
初始化模块示例数据

### 16.2 方法说明

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `init_sample_customers()` | - | Dict | 初始化客户模块示例数据 |

> **注意**：当前 SampleDataService 仅包含 `init_sample_customers()` 方法。其他服务（clock, smtptest）的 `init_sample_data()` 方法定义在各自的 `modules/*/services.py` 中。

---


