# 全面 Bug 修复与封装重构计划 — 第三批次

> 阶段 5 — 2026-07-08
> 基于全层并行扫描的 22 项执行计划（安全/功能/质量）

---

## 阶段一：🔴 安全与功能修复（5项）

| # | 文件 | 问题 | 方案 | 预估 |
|---|------|------|------|------|
| 1 | `core/decorators.py:69-74` | `api_get_view` / `api_post_view` 使用 `login_required`（302 重定向），JSON API 端点在未认证时返回 HTML | `api_get_view` → `login_required_json(require_GET(...))`；`api_post_view` → `login_required_json(require_POST(...))` | 2min |
| 2 | `core/views/api/cards.py:165` | `navigation_settings` 使用 `@api_get_view`（设计为 JSON 装饰器）但返回 `render()` HTML | 改为 `@login_required` + `@require_GET` | 1min |
| 3 | `core/module/views.py:197` | `module_create_action` 使用 `@admin_post_view`（302 重定向）但返回 JSON | 改为 `@admin_required_json` + `@require_POST` | 1min |
| 4 | `core/marketplace/views.py:65` | `market_install` 使用 `@admin_post_view`（302 重定向）但返回 JSON | 改为 `@admin_required_json` + `@require_POST` | 1min |
| 5 | `core/importexport/views.py:380-381` | `do_import` 异常时返回 `json_error()`（JSON），成功时返回 `render()`（HTML），浏览器表单间接收不到 JSON 错误 | 改为 `messages.error()` + `redirect()` | 2min |

---

## 阶段二：🟠 功能降级与不一致修复（8项）

| # | 文件 | 问题 | 方案 | 预估 |
|---|------|------|------|------|
| 6 | `cimf_django/database.py:79` | SQLite `OPTIONS.init_command` 从不执行（Django SQLite 后端忽略此选项），WAL 模式不走此路径 | 移除 `init_command` 行 | 1min |
| 7 | `core/apps.py:13` | WAL 信号处理器只设 `PRAGMA journal_mode=WAL`，缺少 `synchronous=NORMAL` | 添加 `PRAGMA synchronous=NORMAL` | 1min |
| 8 | `config.env:60,62,75` | `DJANGO_DB_TYPE=sqlite` 重复 2 次（行 60 和 62）；孤立的 `SECRET_KEY`（行 75）从未被读取（正确变量为 `DJANGO_SECRET_KEY`） | 删重复行、删孤立行 | 1min |
| 9 | `cimf_django/middleware.py:30` | Logger 名 `"cimf"` 与项目 `__name__` 约定不一致 | 改为 `logging.getLogger(__name__)` | 1min |
| 10 | `core/services/tasks/base.py:126-127` | `except (TypeError, ValueError): pass` 静默吞噬间隔转换失败 | 添加 `logger.warning()` | 1min |
| 11 | `core/node/services/node_type_service.py:141-142` | `except (ImportError, ModuleNotFoundError, AttributeError): pass` 静默吞噬模块加载失败 | 添加 `logger.warning()` | 1min |
| 12 | `core/node/services/node_type_service.py:149-165` | `init_default_node_types()` 循环内对每个节点类型执行独立 `.first()` 查询（N+1） | 预取所有现有 slug 后循环 | 3min |
| 13 | `modules/resident_info/module.py` | 缺少 `install_on_init` 字段；仪表盘卡片缺少 `color_start`/`color_end` | 补充字段：`install_on_init: True`，卡片添加 `"color_start": "#0d6efd"` `"color_end": "#0a58ca"` | 1min |
| 14 | `modules/calc/module.py` | 缺少 `require` 字段 | 添加 `require: []` | 1min |
| 15 | `modules/smtptest/module.py` | 缺少 `require`、`frontpage_card_clickable` 字段 | 添加 `require: []`、`frontpage_card_clickable: False` | 1min |

---

## 阶段三：🟢 代码质量与整合（7项）

| # | 文件 | 问题 | 方案 | 预估 |
|---|------|------|------|------|
| 16 | `modules/customer/views.py:33` + `modules/resident_info/views.py:19` | 重复的 `safe_int()` 函数，两份实现需同步维护 | 移至 `core/utils/views.py`，引入后删除重复定义 | 3min |
| 17 | `modules/resident_info/views.py:86-88` | 使用原始 `Paginator` 而非共享的 `paginate_queryset()`，缺少中心化分页处理 | 切换为 `from core.utils.pagination import paginate_queryset` | 2min |
| 18 | `modules/resident_info/views.py`（多处） | `Http404`、`PermissionService` 在函数体内惰性导入 | 移入文件顶部导入 | 2min |
| 19 | `core/views/auth.py:52` | `logout_view` 缺少 `@login_required`（未认证用户也可 POST 到 `/logout/`） | 添加 `@login_required` | 1min |
| 20 | `core/services/sample_data_service.py:34-35` | 可选模块导入失败时无日志 | 添加 `logger.debug()` | 1min |
| 21 | `core/node/models.py:64-65` | `Node.__str__` 返回 `f"Node {self.id} ({self.node_type_id})"`，缺乏可读上下文 | 改进为包含 `node_type.name` 或 owner 信息 | 1min |
| 22 | 各处误报代码注释 | 对 `@require_POST`、`safe_int()`、`api_get_view` 等加入注释说明设计意图 | 加注释标记设计意图和待整合提示 | 2min |

---

## 总计

| 阶段 | 项数 | 预估时间 |
|------|:----:|:--------:|
| 阶段一（🔴 安全/功能） | 5 | 7min |
| 阶段二（🟠 降级/不一致） | 10 | 12min |
| 阶段三（🟢 代码质量） | 7 | 12min |
| **合计** | **22** | **~31min** |
