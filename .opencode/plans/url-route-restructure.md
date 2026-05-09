# URL 路由重组与 /api/ 重复路由清理计划

## 目标

1. **路由分类重组**：按业务域重新组织 `core/urls.py` 中的路由分组
2. **清理重复 API 路由**：删除 `core/urls.py` 中与 `api_urls.py`（`/api/v1/`）完全重复的 14 条路由
3. **迁移 cron API**：将 cron 相关 API 从 `core/urls.py` 迁移到 `api_urls.py`，统一挂载到 `/api/v1/cron/`
4. **更新硬编码路径**：将模板和 JS 中的 `/api/` 路径统一改为 `/api/v1/`

## Phase 1: core/urls.py 路由重组与清理

### 新分组顺序

| 顺序 | 分组 | 路径前缀 |
|------|------|----------|
| 1 | 认证 | `accounts/` |
| 2 | 仪表盘 | `` (根路径) |
| 3 | 内容结构 | `structure/` |
| 4 | 协作工具 | `tools/` |
| 5 | 系统管理 | `system/`（合并 admin + SMTP + 日志 + Cron 管理） |
| 6 | 个人中心 | `user/` |
| 7 | API | `api/`（仅保留 cron 之外的独有路由，待 Phase 2 后全部删除） |
| 8 | 健康检查 | `health/` |
| 9 | 旧路径重定向 | 兼容跳转 |

### 删除的路由（17 条）

- `api/cron/status/`, `api/cron/run/<name>/`, `api/cron/toggle/<name>/` → 迁移到 api_urls.py
- `api/time/current/`, `api/time/test/`, `api/time/status/` → 已存在于 api/v1/
- `api/regions/provinces/`, `api/regions/cities/`, `api/regions/districts/`, `api/regions/search/`, `api/regions/path/`, `api/regions/stats/` → 已存在于 api/v1/
- `api/user/dashboard/cards/`, `api/user/dashboard/cards/save/` → 已存在于 api/v1/
- `api/user/nav-cards/`, `api/user/nav-cards/save/` → 已存在于 api/v1/
- `api/version/` → 已存在于 api/v1/

## Phase 2: api_urls.py 新增 cron API 路由

```python
path('cron/status/', views.cron_status, name='api_cron_status'),
path('cron/run/<str:task_name>/', views.cron_run_task, name='api_cron_run_task'),
path('cron/toggle/<str:task_name>/', views.cron_toggle_task, name='api_cron_toggle_task'),
```

## Phase 3: 更新硬编码路径

### 模板文件（4 个）

| 文件 | 旧路径 | 新路径 |
|------|--------|--------|
| `system_cron_manager.html:110` | `/api/cron/run/` | `/api/v1/cron/run/` |
| `system_cron_manager.html:143` | `/api/cron/toggle/` | `/api/v1/cron/toggle/` |
| `nav_cards_area.html:186` | `/api/user/nav-cards/` | `/api/v1/user/nav-cards/` |
| `dashboard_cards_area.html:199` | `/api/user/dashboard/cards/save/` | `/api/v1/user/dashboard/cards/save/` |
| `dashboard_cards_area.html:367` | `/api/user/dashboard/cards/` | `/api/v1/user/dashboard/cards/` |

### JS 文件（2 个）

| 文件 | 旧路径 | 新路径 |
|------|--------|--------|
| `common.js:146` | `/api/time/current` | `/api/v1/time/current` |
| `dashboard_cards.js:13` | `/api/user/dashboard/cards/` | `/api/v1/user/dashboard/cards/` |
| `dashboard_cards.js:186` | `/api/user/dashboard/cards/save/` | `/api/v1/user/dashboard/cards/save/` |

## Phase 4: 验证

1. `manage.py check` 无错误
2. `./venv/bin/python -c` 验证所有 URL name 正常 reverse
3. `collectstatic` 同步静态文件
4. `update_progress.py` 更新进度
