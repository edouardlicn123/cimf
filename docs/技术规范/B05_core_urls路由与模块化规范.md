# core/urls 路由与模块化规范

> 文档版本：3.0
> 最后更新：2026-05-08

## 一、概述

### 1.1 模块定位
URL 路由层负责将 HTTP 请求映射到对应的视图函数。

### 1.2 设计原则
- **RESTful**：使用语义化的 URL 路径
- **命名规范**：使用 `name='...'` 为每个路由命名
- **分组管理**：按功能模块分组，使用前缀区分
- **命名空间**：每个路由文件定义 `app_name`，使用 `namespace:名` 反向解析
- **路径前缀**：管理后台使用 `/system/`，API 使用 `/api/v1/`，内容结构使用 `/structure/`，事务节点使用 `/nodes/`

## 二、路由分布

### 2.1 路由文件清单

| 文件 | 路由数量 | 命名空间 | 挂载路径 |
|------|----------|----------|----------|
| `core/urls.py` | ~43 | `core` | `/` |
| `core/node/urls.py` | 6 | `node` | `/nodes/` |
| `core/module/urls.py` | 7 | `module` | `/modules/manage/` |
| `core/marketplace/urls.py` | 2 | `market` | `/modules/market/` |
| `core/api_urls.py` | 19 | `api` | `/api/v1/` |
| `core/importexport/urls.py` | 12 | `importexport` | `/importexport/` |
| `modules/urls.py` | 动态 | `modules` | `/system/`（system 类型）、`/modules/`（其它类型） |

### 2.2 根 URL 配置
根配置在 `cimf_django/urls.py`，`include` 所有子路由：`admin/`、`''`(core)、`modules/manage/`、`modules/market/`、`modules/`、`nodes/`、`importexport/`、`api/v1/`。

### 2.3 命名空间汇总

| 命名空间 | 前缀 | 说明 |
|----------|------|------|
| `core` | `/` | 核心应用（认证、管理、内容结构、工具、个人中心、健康检查） |
| `node` | `/nodes/` | 事务节点系统 |
| `module` | `/modules/manage/` | 模块管理 |
| `market` | `/modules/market/` | 模块市场 |
| `modules` | `/system/<slug>/` 或 `/modules/<slug>/` | 动态模块 |
| `api` | `/api/v1/` | REST API |
| `importexport` | `/importexport/` | 数据导入导出 |

## 三、core/urls.py 路由清单

~43 条路由，命名空间 `core`，挂载于 `/`，按功能分 7 组：

| 分组 | 路径前缀 | 路由数量 | 命名模式 |
|------|----------|----------|----------|
| 认证 | `accounts/` | 2 | `core:login`, `core:logout` |
| 仪表盘 | `` | 1 | `core:dashboard` |
| 内容结构 | `structure/` | 14 | `core:structure_dashboard`, `core:node_types_*`, `core:field_types*`, `core:taxonom*` |
| 协作工具 | `tools/` | 2 | `core:tools_index`, `core:tools_page` |
| 系统管理 | `system/` | 15 | `core:system_users`, `core:user_*`, `core:system_*`, `core:cron_*`, `core:smtp_*`, `core:logs_*` |
| 个人中心 | `user/` | 4 | `core:profile_*`, `core:homepage_settings`, `core:navigation_settings` |
| 健康检查 | `health/` | 2 | `core:health_check`, `core:detailed_health_check` |
| 重定向 | — | 3 | 向后兼容旧路径（`structure/`→`/structure/dashboard/` 等） |

## 四、core/node/urls.py 路由清单

6 条路由，命名空间 `node`，挂载于 `/nodes/`，CRUD 由 `module_dispatch` 分发：

| 路径 | 视图 | 名称 (name) |
|------|------|-------------|
| `dashboard/` | `nodes_index` | `index` |
| `<slug>/create/` | `module_dispatch` | `node_create` |
| `<slug>/` | `module_dispatch` | `module_page` |
| `<slug>/<id>/` | `module_dispatch` | `node_view` |
| `<slug>/<id>/edit/` | `module_dispatch` | `node_edit` |
| `<slug>/<id>/delete/` | `module_dispatch` | `node_delete` |

## 五、其他路由模块清单

### 5.1 模块管理（namespace: `module`，前缀：`/modules/manage/`）
7 条路由，命名模式 `module:list` / `module:scan` / `module:create` / `module:create_action` / `module:install` / `module:enable` / `module:disable`。

### 5.2 模块市场（namespace: `market`，前缀：`/modules/market/`）
2 条路由：`market:index`, `market:install`。

### 5.3 导入导出（namespace: `importexport`，前缀：`/importexport/`）
12 条路由，分 export 和 import 两组：`export_list` / `export_select_fields` / `export_confirm` / `export_exporting` / `do_export` 和 `import_list` / `import_page` / `download_template` / `upload_preview` / `do_import` / `download_errors`，加首页 `importexport_dashboard`。

### 5.4 REST API（namespace: `api`，前缀：`/api/v1/`）
19 条路由，分组如下：
- **cron**（3）：`api_cron_status`, `api_cron_run_task`, `api_cron_toggle_task`
- **time**（3）：`api_time_current`, `api_time_test`, `api_time_status`
- **regions**（6）：`api_regions_provinces`, `api_regions_cities`, `api_regions_districts`, `api_regions_search`, `api_regions_path`, `api_regions_stats`
- **user**（4）：`api_dashboard_cards`, `api_dashboard_cards_save`, `api_nav_cards`, `api_nav_cards_save`
- **system**（3）：`api_health_check`, `api_detailed_health_check`, `api_version`

### 5.5 动态模块路由（namespace: `modules`）
| 模块 | 类型 | 路由前缀 | 路由机制 |
|------|------|----------|----------|
| customer | node | `nodes/customer/` | `core/node/urls.py` 分发 |
| clock | system | `system/clock/` | 动态挂载于 `modules` 命名空间 |
| calc | tool | `tools/calc/` | `core/urls.py` `tools_page` 分发 |
| smtptest | tool | `tools/smtptest/` | `core/urls.py` `tools_page` 分发 |

### 5.6 模块通用 API
`api/taxonomy-items/` → `taxonomy_items_api`（视图来自 `core/node/views.py`），挂载于 `modules` 命名空间。

## 六、模块分发机制（module_dispatch）

### 6.1 概述
`core/node/views.py` 的 `module_dispatch` 根据 `node_type_slug` 动态加载对应模块视图。

### 6.2 分发规则
```
/nodes/<slug>/[create|<id>|<id>/edit|<id>/delete]
  → module_dispatch(request, node_type_slug, node_id=None, action=None)
    action='create'  → modules.{slug}.views.node_create / create
    action='delete'  → modules.{slug}.views.node_delete / delete
    通用分发          → module_view / detail_view / list_view / node_list / node_view / node_edit
    fallback          → redirect('node:module_page', node_type_slug)
```

### 6.3 视图函数优先级
| 操作 | 优先查找 | 备选 |
|------|----------|------|
| list | `node_list` | `list_view` |
| create | `node_create` | `create` |
| view | `module_view` | `detail_view`, `node_view` |
| edit | `node_edit` | — |
| delete | `node_delete` | `delete` |

## 七、URL 命名规范

### 7.1 命名空间
在每个 `urls.py` 中定义 `app_name = 'xxx'`。

### 7.2 模板中使用
Jinja2 语法：`{{ url('namespace:name', arg) }}`。示例：`url('core:system_users')`、`url('core:taxonomy_view', taxonomy.id)`、`url('node:node_edit', node_type.slug, node.id)`。

### 7.3 视图中使用
`redirect('namespace:name', kwarg=val)` 或 `reverse('namespace:name')`。示例：`redirect('core:system_users')`、`reverse('api:api_cron_run_task', kwargs={'task_name': 'sync_time'})`。

## 八、路径分组规范

### 8.1 前缀约定

| 前缀 | 用途 | 示例 |
|------|------|------|
| `/system/` | 系统管理 + system 类型模块 | `/system/users/`, `/system/clock/api/time/` |
| `/structure/` | 内容结构（节点类型、词汇表、字段类型） | `/structure/taxonomies/` |
| `/nodes/` | 事务节点（node 类型模块 CRUD） | `/nodes/customer/` |
| `/tools/` | 协作工具（tool 类型模块） | `/tools/calc/` |
| `/modules/manage/` | 模块管理 | `/modules/manage/` |
| `/modules/market/` | 模块市场 | `/modules/market/` |
| `/importexport/` | 导入导出 | `/importexport/export/` |
| `/api/v1/` | REST API | `/api/v1/time/current/` |
| `/user/` | 个人中心 | `/user/profile/` |
| `/health/` | 健康检查 | `/health/` |

## 九、动态路由

### 9.1 模块动态加载
`modules/urls.py` 从数据库查询已安装模块，按类型挂载：system 类型挂到 `system/<slug>/`，其它类型挂到 `modules/<slug>/`；node 和 tool 类型由 core 路由统一分发，不在此挂载。

### 9.2 安全加载
`try_include_module()` 使用 `import_module` 动态导入，失败返回空列表，确保模块缺失时系统不崩溃。

## 十、错误处理配置

### 10.1 全局错误处理器
在 `cimf_django/settings.py` 中配置：`handler400` / `handler403` / `handler404` / `handler500`。

### 10.2 错误视图
| 状态码 | 视图函数 | 模板 |
|--------|----------|------|
| 400 | error_400 | `errors/400.html` |
| 403 | error_403 | `errors/403.html` |
| 404 | error_404 | `errors/404.html` |
| 500 | error_500 | `errors/500.html` |

## 十一、模块路由前缀规范

### 11.1 规则定义

| 模块类型 | 路由前缀 | 路由机制 |
|----------|----------|----------|
| `node` | `nodes/<slug>/` | `core/node/urls.py` → `module_dispatch` |
| `tool` | `tools/<slug>/` | `core/urls.py` → `tools_page` |
| `system` | `system/<slug>/` | `modules/urls.py` 动态挂载 |
| 其它 | `modules/<slug>/` | `modules/urls.py` 动态挂载 |

### 11.2 路由机制说明
- **node**：`module_dispatch` 分发 CRUD；模块自定义 URL 通过 `module_custom_dispatch` 处理；重定向用 `node:*` 命名空间。
- **tool**：`tools_page` 分发单页工具；模块提供 `tool_view(request)`；无需模块 `urls.py`。
- **system**：动态挂载到独立前缀；命名空间 `modules:<app_name>:<name>`。
- **其它**：开发时讨论确定。

### 11.3 命名空间使用规范
| 模块类型 | 视图重定向 | 模板 URL |
|----------|-----------|----------|
| node | `redirect('node:module_page', node_type_slug='xxx')` | `url('node:module_page', slug)` |
| tool | `redirect('core:tools_page', tool_slug='xxx')` | `url('core:tools_page', slug)` |
| system | `redirect('modules:xxx:name')` | `url('modules:xxx:name')` |

### 11.4 模块自定义 URL（node 类型）
自定义 URL 在 `modules/<slug>/urls.py` 中定义，自动挂载于 `nodes/<slug>/` 下，通过 `module_custom_dispatch` 分发。
