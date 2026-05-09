# core/urls 路由与模块化规范

> 文档版本：3.0  
> 创建日期：2026-04-07  
> 最后更新：2026-05-08

---

## 一、概述

### 1.1 模块定位

URL 路由层负责将 HTTP 请求映射到对应的视图函数，是请求入口的第一层分发。

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **RESTful** | 使用语义化的 URL 路径 |
| **命名规范** | 使用 `name='...'` 为每个路由命名，便于 `url('namespace:name')` 调用 |
| **分组管理** | 按功能模块分组，使用前缀区分 |
| **命名空间** | 每个路由文件定义 `app_name`，使用 `namespace:名` 反向解析 |
| **路径前缀** | 管理后台使用 `/system/`，API 使用 `/api/v1/`，内容结构使用 `/structure/`，事务节点使用 `/nodes/` |

---

## 二、路由分布

### 2.1 路由文件清单

| 文件 | 路由数量 | 命名空间 | 挂载路径 |
|------|----------|----------|----------|
| `core/urls.py` | ~43 | `core` | `/` |
| `core/node/urls.py` | 6 | `node` | `/nodes/` |
| `core/module/urls.py` | 7 | `module` | `/modules/manage/` |
| `core/marketplace/urls.py` | 2 | `market` | `/modules/market/` |
| `core/api_urls.py` | 19 | `api` | `/api/v1/` |
| `core/importexport/urls.py` | 12 | `importexport`（在根urls.py中定义） | `/importexport/` |
| `modules/urls.py` | 动态 | `modules` | `/system/`（system 类型）、`/modules/`（其它类型） |

### 2.2 根 URL 配置

在 `cimf_django/urls.py` 中 include 所有子路由：

```python
from django.contrib import admin
from django.urls import path, include
from core.importexport.urls import urlpatterns_all as importexport_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core 应用路由（根路径）
    path('', include('core.urls', namespace='core')),
    
    # 模块管理（必须在 modules/ 之前，避免被动态路由匹配）
    path('modules/manage/', include(('core.module.urls', 'module'), namespace='module')),
    path('modules/market/', include('core.marketplace.urls', namespace='market')),
    path('modules/', include('modules.urls', namespace='modules')),
    
    # 事务节点
    path('nodes/', include('core.node.urls', namespace='node')),
    
    # 导入导出
    path('importexport/', include((importexport_urls, 'importexport'), namespace='importexport')),
    
    # REST API（版本化）
    path('api/v1/', include('core.api_urls', namespace='api')),
]
```

### 2.3 命名空间汇总

| 命名空间 | 前缀 | 说明 |
|----------|------|------|
| `core` | `/` | 核心应用（认证、管理、内容结构、工具、个人中心、健康检查） |
| `node` | `/nodes/` | 事务节点系统 |
| `module` | `/modules/manage/` | 模块管理 |
| `market` | `/modules/market/` | 模块市场 |
| `modules` | `/system/<slug>/` | system 类型模块（如 clock → `system/clock/api/time/`） |
| | `/modules/<slug>/` | 其它类型模块（暂定，待讨论） |
| `api` | `/api/v1/` | REST API |
| `importexport` | `/importexport/` | 数据导入导出 |

---

## 三、core/urls.py 路由清单

### 3.1 认证路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `accounts/login/` | login_view | login | 用户登录 |
| `accounts/logout/` | logout_view | logout | 用户登出 |

### 3.2 仪表盘

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `` (根路径) | dashboard | dashboard | 首页仪表盘 |

### 3.3 内容结构路由（`/structure/`）

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `structure/dashboard/` | structure_dashboard | structure_dashboard | 内容结构首页 |
| `structure/types/` | node_types_list | node_types_list | 节点类型列表 |
| `structure/types/<id>/toggle/` | node_type_toggle | node_type_toggle | 切换类型状态 |
| `structure/types/<id>/delete/` | node_type_delete | node_type_delete | 删除类型 |
| `structure/fieldtypes/` | field_types | field_types | 字段类型文档 |
| `structure/api/fieldtypes/` | field_types_api | field_types_api | 字段类型 API |
| `structure/taxonomies/` | taxonomies | taxonomies | 词汇表列表 |
| `structure/taxonomy/<id>/` | taxonomy_view | taxonomy_view | 查看词汇表 |
| `structure/taxonomy/<id>/edit/` | taxonomy_edit | taxonomy_edit | 编辑词汇表 |
| `structure/taxonomy/create/` | taxonomy_create | taxonomy_create | 创建词汇表 |
| `structure/taxonomy/<id>/delete/` | taxonomy_delete | taxonomy_delete | 删除词汇表 |
| `structure/taxonomy/<id>/item/create/` | taxonomy_item_create | taxonomy_item_create | 创建词汇项 |
| `structure/taxonomy/<id>/item/<id>/edit/` | taxonomy_item_update | taxonomy_item_update | 编辑词汇项 |
| `structure/taxonomy/<id>/item/<id>/delete/` | taxonomy_item_delete | taxonomy_item_delete | 删除词汇项 |

### 3.4 协作工具路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `tools/dashboard/` | tools_index | tools_index | 工具总览 |
| `tools/<slug>/` | tools_page | tools_page | 工具页面（动态） |

### 3.5 系统管理路由（`/system/`）

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `system/` | admin_dashboard | admin_dashboard | 管理后台首页 |
| `system/users/` | system_users | system_users | 用户管理列表 |
| `system/user/create/` | user_create | user_create | 创建用户 |
| `system/user/<id>/edit/` | user_edit | user_edit | 编辑用户 |
| `system/user/<id>/delete/` | user_delete | user_delete | 删除用户 |
| `system/settings/` | system_settings | system_settings | 系统设置 |
| `system/permissions/` | system_permissions | system_permissions | 权限管理 |
| `system/cron/` | cron_manager | cron_manager | 定时任务管理 |
| `system/permission-check/` | permission_check | permission_check | 权限检查 |
| `system/smtp/` | smtp_config | smtp_config | SMTP 配置 |
| `system/smtp/test/` | smtp_test | smtp_test | 测试发送 |
| `system/smtp/history/` | smtp_history | smtp_history | 发送历史 |
| `system/smtp/cleanup/` | smtp_cleanup_logs | smtp_cleanup_logs | 清理日志 |
| `system/logs/` | logs_index | logs_index | 日志首页 |
| `system/logs/<type>/` | logs_view | logs_view | 查看指定日志 |

### 3.6 个人中心路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `user/profile/` | profile_view | profile_view | 个人资料 |
| `user/settings/` | profile_settings | profile_settings | 个人设置 |
| `user/functioncards/` | homepage_settings | homepage_settings | 功能卡片设置 |
| `user/navcards/` | navigation_settings | navigation_settings | 导航卡片设置 |

### 3.7 健康检查路由

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `health/` | health_check | health_check | 健康检查 |
| `health/detailed/` | detailed_health_check | detailed_health_check | 详细检查 |

### 3.8 旧路径重定向（向后兼容）

| 旧路径 | 重定向到 | 说明 |
|--------|----------|------|
| `structure/` | `/structure/dashboard/` | 内容结构首页 |
| `taxonomies/` | `/structure/taxonomies/` | 词汇表 |
| `taxonomy/` | `/structure/taxonomies/` | 词汇表（无 ID） |

---

## 四、core/node/urls.py 路由清单

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `dashboard/` | nodes_index | index | 事务首页 |
| `<slug>/create/` | module_dispatch | node_create | 创建节点（动态分发） |
| `<slug>/` | module_dispatch | module_page | 节点列表（动态分发） |
| `<slug>/<id>/` | module_dispatch | node_view | 查看节点（动态分发） |
| `<slug>/<id>/edit/` | module_dispatch | node_edit | 编辑节点（动态分发） |
| `<slug>/<id>/delete/` | module_dispatch | node_delete | 删除节点（动态分发） |

**动态分发说明**：所有节点 CRUD 路由由 `core.node.views.module_dispatch` 统一分发，根据 `node_type_slug` 加载对应模块的视图函数。详见第六节。

---

## 五、其他路由模块清单

### 5.1 模块管理（namespace: `module`，前缀：`/modules/manage/`）

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `` | modules_manage | list | 模块列表 |
| `scan/` | module_scan | scan | 扫描模块 |
| `create/` | module_create | create | 创建模块 |
| `create/action/` | module_create_action | create_action | 创建操作（AJAX） |
| `install/<id>/` | module_install | install | 安装模块 |
| `enable/<id>/` | module_enable | enable | 启用模块 |
| `disable/<id>/` | module_disable | disable | 禁用模块 |

### 5.2 模块市场（namespace: `market`，前缀：`/modules/market/`）

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `` | market_index | index | 市场首页 |
| `install/<id>/` | market_install | install | 安装模块 |

### 5.3 导入导出（namespace: `importexport`，前缀：`/importexport/`）

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `` | importexport_dashboard | importexport_dashboard | 首页 |
| `export/` | export_list | export_list | 导出列表 |
| `export/<slug>/` | export_select_fields | export_select_fields | 选择字段 |
| `export/<slug>/confirm/` | export_confirm | export_confirm | 确认导出 |
| `export/<slug>/exporting/` | export_exporting | export_exporting | 导出中 |
| `export/<slug>/do/` | do_export | do_export | 执行导出 |
| `import/` | import_list | import_list | 导入列表 |
| `import/<slug>/` | import_page | import_page | 导入页面 |
| `import/<slug>/template/` | download_template | download_template | 下载模板 |
| `import/<slug>/upload/` | upload_preview | upload_preview | 上传预览 |
| `import/<slug>/do/` | do_import | do_import | 执行导入 |
| `import/<slug>/errors/` | download_errors | download_errors | 下载错误 |

### 5.4 REST API（namespace: `api`，前缀：`/api/v1/`）

| 路径 | 视图 | 名称 (name) | 说明 |
|------|------|-------------|------|
| `cron/status/` | cron_status | api_cron_status | Cron 状态 |
| `cron/run/<name>/` | cron_run_task | api_cron_run_task | 执行任务 |
| `cron/toggle/<name>/` | cron_toggle_task | api_cron_toggle_task | 切换任务 |
| `time/current/` | api_time_current | api_time_current | 当前时间 |
| `time/test/` | api_time_test | api_time_test | 测试时间 |
| `time/status/` | api_time_status | api_time_status | 时间状态 |
| `regions/provinces/` | api_regions_provinces | api_regions_provinces | 省份 |
| `regions/cities/` | api_regions_cities | api_regions_cities | 城市 |
| `regions/districts/` | api_regions_districts | api_regions_districts | 区县 |
| `regions/search/` | api_regions_search | api_regions_search | 搜索 |
| `regions/path/` | api_regions_path | api_regions_path | 路径 |
| `regions/stats/` | api_regions_stats | api_regions_stats | 统计 |
| `user/dashboard/cards/` | api_dashboard_cards | api_dashboard_cards | 功能卡片 |
| `user/dashboard/cards/save/` | api_dashboard_cards_save | api_dashboard_cards_save | 保存卡片 |
| `user/nav-cards/` | api_nav_cards | api_nav_cards | 导航卡片 |
| `user/nav-cards/save/` | api_nav_cards_save | api_nav_cards_save | 保存导航 |
| `health/` | health_check | api_health_check | 健康检查 |
| `health/detailed/` | detailed_health_check | api_detailed_health_check | 详细检查 |
| `version/` | api_version | api_version | 版本信息 |

### 5.5 动态模块路由（namespace: `modules`）

根据模块类型使用不同的路由前缀，详见第十二章"模块路由前缀规范"：

| 模块 | 类型 | 路由前缀 | 说明 |
|------|------|----------|------|
| customer | node | `nodes/customer/` | 通过 `core/node/urls.py` 分发 |
| clock | system | `system/clock/` | 动态挂载于 `modules` 命名空间 |
| calc | tool | `tools/calc/` | 通过 `core/urls.py` `tools_page` 分发 |
| smtptest | tool | `tools/smtptest/` | 通过 `core/urls.py` `tools_page` 分发 |

### 5.6 模块通用 API（namespace: `modules`）

> 注：以下 API 路由挂载于 `/modules/` 路径下，但视图函数可能来自 core。

| 路径 | 视图 | 名称 (name) | 视图来源 | 说明 |
|------|------|-------------|----------|------|
| `api/taxonomy-items/` | taxonomy_items_api | taxonomy_items_api | `core/node/views.py` | 词汇项 API |

---

## 六、模块分发机制（module_dispatch）

### 6.1 概述

`core/node/views.py` 中的 `module_dispatch` 是节点系统的核心分发器。所有 `/nodes/` 下的 CRUD 路由均指向此函数，它根据 `node_type_slug` 动态加载对应模块的视图函数。

### 6.2 分发规则

```
请求: /nodes/<slug>/[create|<id>|<id>/edit|<id>/delete]
  │
  ▼
module_dispatch(request, node_type_slug, node_id=None, action=None)
  │
  ├── action='create'  → 优先调用 modules.{slug}.views.node_create(request)
  │                       备选: create(request)
  ├── action='delete'  → 优先调用 modules.{slug}.views.node_delete(request, node_id)
  │                       备选: delete(request, node_id)
  ├── 通用分发          → 优先调用 modules.{slug}.views.module_view(request, node_id)
  │                       备选1: detail_view(request, node_id)（有 node_id 时）
  │                       备选2: list_view(request)
  │                       备选3: node_list(request)（无 node_id 时）
  │                       备选4: node_view(request, node_id)（有 node_id 时）
  │                       备选5: node_edit(request, node_id)（有 node_id 时）
  └── fallback          →  redirect('node:module_page', node_type_slug)
```

### 6.3 视图函数优先级

| 操作 | 优先查找 | 备选 |
|------|----------|------|
| list | `node_list` | `list_view` |
| create | `node_create` | `create` |
| view | `module_view` | `detail_view`、`node_view` |
| edit | `node_edit` | — |
| delete | `node_delete` | `delete` |

### 6.4 模块视图函数示例

```python
# modules/customer/views.py
@login_required
def node_list(request):
    """客户列表"""
    return render(request, 'list.html', {...})

@login_required
def node_create(request):
    """创建客户"""
    if request.method == 'POST':
        CustomerService.create(request.user, request.POST.dict())
        return redirect('node:module_page', node_type_slug='customer')
    return render(request, 'edit.html', {'customer': None})

@login_required
def node_view(request, node_id):
    """查看客户"""
    customer = CustomerService.get_by_node_id(node_id)
    return render(request, 'view.html', {'customer': customer})

@login_required
def node_edit(request, node_id):
    """编辑客户"""
    customer = CustomerService.get_by_node_id(node_id)
    if request.method == 'POST':
        CustomerService.update(customer.id, request.user, request.POST.dict())
        return redirect('node:node_view', node_type_slug='customer', node_id=node_id)
    return render(request, 'edit.html', {'customer': customer})

@login_required
def node_delete(request, node_id):
    """删除客户"""
    CustomerService.delete(node_id)
    return redirect('node:module_page', node_type_slug='customer')
```

---

## 七、URL 命名规范

### 7.1 命名空间

在 `urls.py` 中定义 `app_name`：

```python
# core/urls.py
app_name = 'core'
```

### 7.2 模板中使用

项目使用 **Jinja2** 模板引擎，使用 `url()` 函数：

```html
<!-- 跳转链接 -->
<a href="{{ url('core:system_users') }}">用户管理</a>

<!-- 带参数 -->
<a href="{{ url('core:taxonomy_view', taxonomy.id) }}">查看</a>

<!-- 多参数 -->
<a href="{{ url('node:node_edit', node_type.slug, node.id) }}">编辑</a>
```

### 7.3 视图中使用

```python
from django.urls import reverse

# 重定向（字符串形式，Django 自动解析命名空间）
return redirect('core:system_users')
return redirect('node:module_page', node_type_slug='customer')

# 反向解析（带命名空间）
url = reverse('core:taxonomy_view', args=[taxonomy_id])
url = reverse('api:api_cron_run_task', kwargs={'task_name': 'sync_time'})
```

---

## 八、路径分组规范

### 8.1 前缀约定

| 前缀 | 用途 | 示例 |
|------|------|------|
| `/system/` | 系统管理（后台、SMTP、日志）+ system 类型模块 | `/system/users/`, `/system/cron/`, `/system/clock/api/time/` |
| `/structure/` | 内容结构（节点类型、词汇表、字段类型） | `/structure/taxonomies/` |
| `/nodes/` | 事务节点（node 类型模块 CRUD） | `/nodes/customer/` |
| `/tools/` | 协作工具（tool 类型模块） | `/tools/dashboard/`, `/tools/calc/` |
| `/modules/manage/` | 模块管理 | `/modules/manage/` |
| `/modules/market/` | 模块市场 | `/modules/market/` |
| `/importexport/` | 导入导出 | `/importexport/export/` |
| `/api/v1/` | REST API | `/api/v1/time/current/` |
| `/user/` | 个人中心 | `/user/profile/` |
| `/health/` | 健康检查 | `/health/` |

**模块路由前缀规则**：详见第十一章"模块路由前缀规范"。

---

## 九、动态路由

### 9.1 模块动态加载

`modules/urls.py` 从数据库动态注册模块路由：

```python
def get_installed_module_slugs():
    """动态获取所有已安装模块的信息"""
    try:
        from core.module.models import Module
        modules = Module.objects.filter(is_installed=True, is_active=True)
        return [(m.module_id, m.module_type) for m in modules]
    except Exception:
        return []

def get_dynamic_routes():
    """根据模块类型分前缀动态挂载模块路由"""
    modules = get_installed_module_slugs()
    routes = []
    for mod_slug, mod_type in modules:
        if mod_type == 'node':
            # node 类型由 core/node/urls.py 分发，跳过
            continue
        elif mod_type == 'tool':
            # tool 类型由 core/urls.py tools_page 分发，跳过
            continue
        elif mod_type == 'system':
            # system 类型挂载到 system/<slug>/
            routes.extend(try_include_module(mod_slug, prefix='system/'))
        else:
            # 其它类型挂载到 modules/<slug>/（暂定）
            routes.extend(try_include_module(mod_slug, prefix='modules/'))
    return routes

urlpatterns = get_dynamic_routes() + [
    path('api/taxonomy-items/', node_views.taxonomy_items_api, name='taxonomy_items_api'),
]
```

### 9.2 安全加载

使用 `try_include_module` 确保模块缺失时系统仍可启动：

```python
def try_include_module(module_slug, prefix=''):
    """尝试动态导入模块 URL，失败则返回空列表"""
    try:
        import_module(f'modules.{module_slug}.urls')
        return [path(f'{prefix}{module_slug}/', include(f'modules.{module_slug}.urls'))]
    except (ImportError, ModuleNotFoundError, AttributeError):
        return []
```

---

## 十、错误处理配置

### 10.1 全局错误处理器

在 `cimf_django/settings.py` 中配置：

```python
handler400 = 'core.views.error_400'
handler403 = 'core.views.error_403'
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
```

### 10.2 错误视图

| 状态码 | 视图函数 | 模板 |
|--------|----------|------|
| 400 | error_400 | `errors/400.html` |
| 403 | error_403 | `errors/403.html` |
| 404 | error_404 | `errors/404.html` |
| 500 | error_500 | `errors/500.html` |

---

## 十一、模块路由前缀规范

### 11.1 规则定义

模块的 URL 路由前缀由模块类型（`module_type`）决定：

| 模块类型 | 路由前缀 | 路由机制 | 示例 |
|----------|----------|----------|------|
| `node` | `nodes/<slug>/` | `core/node/urls.py` → `module_dispatch` 分发 | `nodes/customer/` |
| `tool` | `tools/<slug>/` | `core/urls.py` → `tools_page` 分发 | `tools/calc/` |
| `system` | `system/<slug>/` | `modules/urls.py` 动态挂载（`modules` 命名空间） | `system/clock/api/time/` |
| 其它 | `modules/<slug>/` | `modules/urls.py` 动态挂载（`modules` 命名空间） | 暂定，待讨论 |

### 11.2 路由机制说明

#### node 类型
- 通过 `core/node/urls.py` 中的 `module_dispatch` 统一分发
- 支持标准 CRUD：列表、创建、查看、编辑、删除
- 模块自定义 URL（如 `api/stats/`）通过 `core/node/views.py` 的 `module_custom_dispatch` 处理
- 模块 `views.py` 中的重定向应使用 `node:*` 命名空间

#### tool 类型
- 通过 `core/urls.py` 中的 `tools_page` 动态分发
- 提供单页工具界面
- 模块 `views.py` 应提供 `tool_view(request)` 函数
- 不需要模块级别的 `urls.py`

#### system 类型
- 通过 `modules/urls.py` 动态挂载，享用自己的路由前缀
- 使用 `modules:<app_name>:<name>` 命名空间
- 如 clock 模块：`system/clock/api/time/` 对应 `modules:clock:api_time`

#### 其它类型
- 开发时讨论确定路由前缀和机制
- 当前暂挂载于 `modules/<slug>/`

### 11.3 命名空间使用规范

| 模块类型 | 视图重定向 | 模板 URL 生成 |
|----------|-----------|---------------|
| node | `redirect('node:module_page', node_type_slug='xxx')` | `url('node:module_page', slug)` |
| tool | `redirect('core:tools_page', tool_slug='xxx')` | `url('core:tools_page', slug)` |
| system | `redirect('modules:xxx:name')` | `url('modules:xxx:name')` |

### 11.4 模块自定义 URL（node 类型）

node 类型模块如需自定义 URL（超出标准 CRUD 范围），需要在 `modules/<slug>/urls.py` 中定义：
- 自定义 URL 会自动挂载于 `nodes/<slug>/` 下
- 通过 `core/node/views.py` 的 `module_custom_dispatch` 动态解析
- 示例：customer 模块的 `api/stats/` 可通过 `nodes/customer/api/stats/` 访问

---

## 十二、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2026-04-07 | 初始版本 |
| 1.1 | 2026-05-03 | 添加导入导出、模块市场路由 |
| 1.2 | 2026-05-03 | 全面重组：/node/→/nodes/、/api/→/api/v1/、/taxonomies/→/structure/taxonomies/、新增 module_dispatch 分发机制、删除重复 API 路由、新增旧路径重定向 |
| 1.3 | 2026-05-03 | 修正路由计数（core/urls: ~40→~42, api_urls: ~18→19, importexport: ~13→12）、补充 calc 和 smtptest 模块到动态路由表 |
| 1.4 | 2026-05-04 | 修正模块通用 API 说明，标注 taxonomy_items_api 视图来源为 core/node/views.py |
| 1.5 | 2026-05-04 | 更新 module_dispatch 分发规则（含 module_view/detail_view/list_view 备选链）、修正视图优先级表（view 优先 module_view 而非 node_view） |
| 1.6 | 2026-05-06 | 修正API路由计数(19→17→修正回19)、标注importexport namespace来源 |
| 1.7 | 2026-05-06 | 修正API路由计数回19（此前误改为17） |
| 1.8 | 2026-05-06 | 修正core/urls.py路由计数~42→~43 |
| 1.9 | 2026-05-06 | 修正根URL配置代码示例，补全admin导入和core路由 |
| 3.0 | 2026-05-08 | 新增第十一章"模块路由前缀规范"，按模块类型分配路由前缀：node→nodes/、tool→tools/、system→system/、其它→modules/（暂定） |
