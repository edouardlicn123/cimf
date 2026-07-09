# core/views 视图层规范

> 文档版本：2.3  
> 创建日期：2026-04-07  
> 最后更新：2026-05-06

---

## 一、概述

### 1.1 模块定位

视图层（Views）是 Django 的请求处理入口，负责接收 HTTP 请求、调用服务层逻辑、返回响应。

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **权限控制** | 使用 `@login_required` 装饰器保护需要认证的视图 |
| **服务调用** | 视图层不直接操作 Model，通过服务层访问 |
| **错误处理** | 使用 `messages` 框架反馈操作结果 |
| **返回类型** | 使用 `render()` 返回模板页面，使用 `JsonResponse` 返回 API |

### 1.3 视图分布

**core/views/ 包**（已拆分为多个模块文件）：

| 文件 | 视图数量 | 主要功能 |
|------|----------|----------|
| `core/views/auth.py` | 2 | 登录、登出 |
| `core/views/dashboard.py` | 2 | 仪表盘（首页、管理后台） |
| `core/views/users.py` | 4 | 用户管理（创建、编辑、删除） |
| `core/views/settings.py` | 7 | 系统设置、个人设置、偏好、权限检查、密码修改 |
| `core/views/taxonomy.py` | 8 | 词汇表管理 |
| `core/views/cron.py` | 5 | 定时任务管理（cron_manager + 3 API + permission_check）+ 3辅助函数 |
| `core/views/importexport.py` | 1 | 导入导出仪表盘 |
| `core/views/tools.py` | 2 | 协作工具页面（tools_index + tools_page）+ 1装饰器 + 1辅助函数 |
| `core/views/node.py` | 1 | 内容结构首页 |
| `core/views/logs.py` | 3 | 日志首页、查看日志、日志API |
| `core/views/errors.py` | 4 | 错误处理视图 |
| `core/views/health.py` | 3 | 健康检查 + API 版本 |
| `core/views/api/` | 19 | REST API 视图（cards:2 + nav-cards:2 + regions:6 + time:3 + cron:3 + health:2 + version:1） |

**其他视图模块**：

| 文件 | 视图数量 | 主要功能 |
|------|----------|----------|
| `core/node/views.py` | 14 | 节点系统（node CRUD、module_dispatch、字段类型） |
| `core/smtp/views.py` | 5 | 邮件配置、预设、发送记录、清理日志 |
| `core/marketplace/views.py` | 2 | 模块市场 |
| `core/module/views.py` | 7 | 模块管理 |
| `modules/customer/views.py` | 6 | 海外客户管理 |
| `modules/clock/views.py` | 1 | 时钟 API |
| `modules/calc/views.py` | 2 | 计算器工具页面 + 计算表达式API |
| `modules/smtptest/views.py` | 2 | 列表页 + 详情页（预留） |

---

## 二、core/views/ 视图清单

### 2.1 认证视图

| 视图函数 | URL | 方法 | 说明 |
|----------|-----|------|------|
| `login_view` | `/accounts/login/` | GET/POST | 用户登录 |
| `logout_view` | `/accounts/logout/` | GET | 用户登出 |

### 2.2 SMTP 邮件视图（core/smtp/views.py）

| 视图函数 | URL | 方法 | 说明 |
|----------|-----|------|------|
| `smtp_config` | `/system/smtp/` | GET/POST | SMTP 配置 |
| `smtp_test` | `/system/smtp/test/` | POST | 发送测试邮件 |
| `smtp_presets` | `/system/smtp/presets/` | GET | 预设配置列表（⚠️ 函数存在但未注册URL，预留功能） |
| `smtp_history` | `/system/smtp/history/` | GET | 发送历史 |
| `smtp_cleanup_logs` | `/system/smtp/cleanup/` | POST | 清理历史记录 |

### 2.3 管理后台视图

| 视图函数 | URL | 方法 | 说明 |
|----------|-----|------|------|
| `admin_dashboard` | `/system/` | GET | 管理后台仪表盘 |
| `system_users` | `/system/users/` | GET | 用户列表 |
| `user_create` | `/system/user/create/` | GET/POST | 创建用户 |
| `user_edit` | `/system/user/<id>/edit/` | GET/POST | 编辑用户 |
| `user_delete` | `/system/user/<id>/delete/` | POST | 删除用户 |
| `system_settings` | `/system/settings/` | GET/POST | 系统设置 |
| `system_permissions` | `/system/permissions/` | GET | 权限管理 |
| `cron_manager` | `/system/cron/` | GET | 定时任务管理 |
| `permission_check` | `/system/permission-check/` | GET | 权限检查页面 |

### 2.4 词汇表视图

| 视图函数 | URL | 方法 | 说明 |
|----------|-----|------|------|
| `taxonomies` | `/structure/taxonomies/` | GET | 词汇表列表 |
| `taxonomy_create` | `/structure/taxonomy/create/` | GET/POST | 创建词汇表 |
| `taxonomy_view` | `/structure/taxonomy/<id>/` | GET | 查看词汇表及词汇项 |
| `taxonomy_edit` | `/structure/taxonomy/<id>/edit/` | GET/POST | 编辑词汇表 |
| `taxonomy_delete` | `/structure/taxonomy/<id>/delete/` | POST | 删除词汇表 |
| `taxonomy_item_create` | `/structure/taxonomy/<id>/item/create/` | POST | 创建词汇项 |
| `taxonomy_item_update` | `/structure/taxonomy/<id>/item/<item_id>/edit/` | POST | 编辑词汇项 |
| `taxonomy_item_delete` | `/structure/taxonomy/<id>/item/<item_id>/delete/` | POST | 删除词汇项 |

### 2.5 个人中心视图

| 视图函数 | URL | 方法 | 说明 |
|----------|-----|------|------|
| `dashboard` | `/` | GET | 仪表盘（首页） |
| `profile_view` | `/user/profile/` | GET | 个人资料查看 |
| `profile_settings` | `/user/settings/` | GET/POST | 个人设置 |
| `homepage_settings` | `/user/functioncards/` | GET/POST | 首页功能卡片设置 |
| `navigation_settings` | `/user/navcards/` | GET | 导航卡片设置 |

### 2.6 API 视图（core/api_urls.py，挂载于 `/api/v1/`）

| 视图函数 | URL | 方法 | 说明 |
|----------|-----|------|------|
| `cron_status` | `/api/v1/cron/status/` | GET | 定时任务状态 |
| `cron_run_task` | `/api/v1/cron/run/<task_name>/` | POST | 手动执行任务 |
| `cron_toggle_task` | `/api/v1/cron/toggle/<task_name>/` | POST | 切换任务启用状态 |
| `api_time_current` | `/api/v1/time/current/` | GET | 获取当前时间 |
| `api_time_test` | `/api/v1/time/test/` | GET | 测试时间同步 |
| `api_time_status` | `/api/v1/time/status/` | GET | 时间同步状态 |
| `api_regions_provinces` | `/api/v1/regions/provinces/` | GET | 获取省份列表 |
| `api_regions_cities` | `/api/v1/regions/cities/` | GET | 获取城市列表 |
| `api_regions_districts` | `/api/v1/regions/districts/` | GET | 获取区县列表 |
| `api_regions_search` | `/api/v1/regions/search/` | GET | 搜索行政区划 |
| `api_regions_path` | `/api/v1/regions/path/` | GET | 获取行政区划路径 |
| `api_regions_stats` | `/api/v1/regions/stats/` | GET | 行政区划统计 |
| `api_dashboard_cards` | `/api/v1/user/dashboard/cards/` | GET | 获取仪表盘卡片 |
| `api_dashboard_cards_save` | `/api/v1/user/dashboard/cards/save/` | POST | 保存仪表盘卡片 |
| `api_nav_cards` | `/api/v1/user/nav-cards/` | GET | 获取导航卡片 |
| `api_nav_cards_save` | `/api/v1/user/nav-cards/save/` | POST | 保存导航卡片 |
| `api_health_check` | `/api/v1/health/` | GET | 健康检查 |
| `api_detailed_health_check` | `/api/v1/health/detailed/` | GET | 详细健康检查 |
| `api_version` | `/api/v1/version/` | GET | API 版本信息 |

### 2.7 API 视图（modules）

| 视图函数 | 模块 | URL | 方法 | 说明 |
|----------|------|-----|------|------|
| `api_time` | clock | `/modules/clock/api/time/` | GET | 获取当前时间（JSON） |
| `api_stats` | customer | `/modules/customer/api/stats/` | GET | 客户统计信息 |

### 2.8 其他视图

| 视图函数 | 来源 | URL | 方法 | 说明 |
|----------|------|-----|------|------|
| `structure_dashboard` | `core/views/node.py` | `/structure/dashboard/` | GET | 内容结构仪表盘 |
| `importexport_dashboard` | `core/views/importexport.py` | `/importexport/` | GET | 导入导出仪表盘 |
| `taxonomy_items_api` | `core/node/views.py` | `/modules/api/taxonomy-items/` | GET | 词汇项 API |

### 2.9 模块分发视图（module_dispatch）

`core/node/views.py` 中的 `module_dispatch` 是节点系统的核心分发器：

```python
@login_required
def module_dispatch(request, node_type_slug, node_id=None, action=None):
    """模块分发视图 - 根据节点类型动态加载对应模块的视图"""
    module_path = node_type_slug
    
    try:
        module_views = __import__(f'modules.{module_path}.views', fromlist=[''])
        
        # create 操作
        if action == 'create':
            if hasattr(module_views, 'node_create'):
                return module_views.node_create(request)
            elif hasattr(module_views, 'create'):
                return module_views.create(request)
        
        # delete 操作
        if action == 'delete':
            if hasattr(module_views, 'node_delete'):
                return module_views.node_delete(request, node_id)
            elif hasattr(module_views, 'delete'):
                return module_views.delete(request, node_id)
        
        # 通用分发
        if hasattr(module_views, 'module_view'):
            return module_views.module_view(request, node_id)
        elif hasattr(module_views, 'detail_view') and node_id:
            return module_views.detail_view(request, node_id)
        elif hasattr(module_views, 'list_view'):
            return module_views.list_view(request)
        elif hasattr(module_views, 'node_list') and not node_id:
            return module_views.node_list(request)
        elif hasattr(module_views, 'node_view') and node_id:
            return module_views.node_view(request, node_id)
        elif hasattr(module_views, 'node_edit') and node_id:
            return module_views.node_edit(request, node_id)
    except ImportError:
        pass
    
    return redirect('node:module_page', node_type_slug)
```

**分发规则**：详见 [B05 规范第六节](./B05_core_urls路由与模块化规范.md#六模块分发机制module_dispatch)

### 2.10 导入导出视图（core/importexport/views.py）

| 视图函数 | URL | 方法 | 说明 |
|----------|-----|------|------|
| `export_list` | `/importexport/export/` | GET | 导出列表 |
| `export_select_fields` | `/importexport/export/<slug>/` | GET/POST | 选择导出字段 |
| `export_confirm` | `/importexport/export/<slug>/confirm/` | GET/POST | 确认导出 |
| `export_exporting` | `/importexport/export/<slug>/exporting/` | GET | 导出中页面 |
| `do_export` | `/importexport/export/<slug>/do/` | GET | 执行导出 |
| `import_list` | `/importexport/import/` | GET | 导入列表 |
| `import_page` | `/importexport/import/<slug>/` | GET | 导入页面 |
| `download_template` | `/importexport/import/<slug>/template/` | GET | 下载模板 |
| `upload_preview` | `/importexport/import/<slug>/upload/` | POST | 上传预览 |
| `do_import` | `/importexport/import/<slug>/do/` | POST | 执行导入 |
| `download_errors` | `/importexport/import/<slug>/errors/` | GET | 下载错误 |

### 2.11 模块市场视图（core/marketplace/views.py）

| 视图函数 | URL | 方法 | 说明 |
|----------|-----|------|------|
| `market_index` | `/modules/market/` | GET | 模块市场首页 |
| `market_install` | `/modules/market/install/<module_id>/` | POST | 安装模块 |

---

## 三、视图规范

### 3.1 权限装饰器

所有需要登录的视图必须使用认证装饰器：

**页面视图**（返回HTML）：
```python
@login_required
def dashboard(request):
    # 视图逻辑
```

**API视图**（返回JSON）：
```python
@login_required_json  # 未登录返回 {"error": "请先登录"} 401
def api_endpoint(request):
    # API逻辑
```

**管理员API**（需要管理员权限）：
```python
@admin_required  # 未登录重定向到dashboard，非管理员重定向+提示
def api_admin_action(request):
    # 管理员页面逻辑
```

需要管理员权限的页面视图，在函数内部进行权限检查：

```python
@login_required
def system_settings(request):
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
```

### 3.2 请求处理模式

视图的标准处理流程：

```python
@login_required
def user_create(request):
    # 1. 权限检查
    if not PermissionService.can_access_admin(request.user):
        messages.error(request, '需要系统管理员权限访问该页面')
        return redirect('core:dashboard')
    
    # 2. GET: 显示表单
    if request.method == 'GET':
        form = UserCreateForm()
        return render(request, 'admin/system_user_edit.html', {
            'form': form,
            'is_create': True,
        })
    
    # 3. POST: 处理表单提交
    form = UserCreateForm(request.POST)
    if form.is_valid():
        # 使用 form.cleaned_data 获取验证后的数据
        try:
            UserService.create_user(**form.cleaned_data)
            messages.success(request, '创建成功')
            return redirect('core:system_users')
        except ValueError as e:
            messages.error(request, str(e))
    
    # 表单验证失败，重新渲染
    return render(request, 'admin/system_user_edit.html', {
        'form': form,
        'is_create': True,
    })
```

> **注意**：项目已全面采用 Django Form 模式处理 POST 数据，不再使用 `request.POST.get()` 手动取值。表单使用 `BootstrapFormMixin` 自动应用 Bootstrap 样式。

### 3.3 错误视图

系统定义了 4 个错误处理视图：

| 视图函数 | 状态码 | 说明 |
|----------|--------|------|
| `error_400` | 400 | Bad Request |
| `error_403` | 403 | Permission Denied |
| `error_404` | 404 | Not Found |
| `error_500` | 500 | Internal Server Error |

在 `urls.py` 中配置：
```python
handler400 = 'core.views.error_400'
handler403 = 'core.views.error_403'
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
```

---

## 四、API 视图规范

### 4.1 JSON 响应格式

```python
# 成功响应
return JsonResponse({'success': True, 'data': {...}})

# 错误响应
return JsonResponse({'success': False, 'error': '错误信息'})
```

### 4.2 分页响应

对于列表类 API，返回分页数据：

```python
return JsonResponse({
    'success': True,
    'data': {
        'items': [...],
        'total': 100,
        'page': 1,
        'page_size': 20,
    }
})
```

---

## 五、视图与服务的交互

### 5.1 调用规范

```python
# 正确：通过服务层获取数据
def dashboard(request):
    stats = UserService.get_user_stats()
    settings = SettingsService.get_all_settings()

# 错误：直接操作 Model
def dashboard(request):
    total = User.objects.count()
```

### 5.2 错误处理

服务层抛出的异常，在视图层捕获并处理：

```python
try:
    UserService.create_user(username=username, password=password)
    messages.success(request, '创建成功')
except ValueError as e:
    messages.error(request, str(e))
```

---

## 六、模板渲染

### 6.1 render 参数

```python
render(request, 'template.html', {
    'context_key': context_value,
    'settings': SettingsService.get_all_settings(),
})
```

### 6.2 公共上下文

以下内容通过 Context Processor 自动注入所有模板：
- `settings`: 系统设置（通过 `system_settings` 上下文处理器）
- `user`: 当前用户
- `perms`: 用户权限（通过 `user_permissions` 上下文处理器）

---

## 七、待补充

- [ ] 补充 node/views.py 视图清单
- [ ] 添加视图单元测试规范
- [ ] 补充视图性能优化建议

---

## 八、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2026-04-07 | 初始版本 |
| 1.1 | 2026-05-02 | 修正 views.py 为 views/ 包结构，更新视图分布表 |
| 1.2 | 2026-05-03 | 修正 SMTP 预设路由、修正 API 路径至 /api/v1/ |
| 1.3 | 2026-05-03 | 修正视图文件计数（cron 5→9, tools 2→5） |
| 1.4 | 2026-05-03 | 修正 SMTP 视图数量 4→5 |
| 1.5 | 2026-05-04 | 修正 logs 视图计数 3→2、修正 node/views 计数 ~15→14、修正 taxonomy_items_api 归类（移至其他视图）、补充导入导出视图来源说明 |
| 1.6 | 2026-05-04 | 修正 logs.py 视图计数 2→3（含 logs_api）、修正 cron.py 计数 9→8（5视图+3辅助）、修正 tools.py 计数 5→4（2视图+装饰器+辅助）、更新 module_dispatch 分发规则代码（含 module_view/detail_view/list_view 备选） |
| 1.7 | 2026-05-06 | 修正 calc/smtptest 模块视图计数（各 1→2） |
| 1.8 | 2026-05-06 | 修正 @admin_required 描述（重定向而非返回JSON） |
| 1.9 | 2026-05-06 | 标注 smtp_presets 为未注册URL的预留功能 |
| 2.0 | 2026-05-06 | 补充 api_urls.py 遗漏的 3 个 API 路由（health/detailed/version）、修正 cards.py 缺失 logging 导入 |
| 2.1 | 2026-05-06 | 修正 module_dispatch 代码示例（补充 module_path 赋值） |
| 2.2 | 2026-05-06 | 修正 API 视图数量描述（14→19，补充详细说明） |
