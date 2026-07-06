# 全面 Bug 修复与封装重构计划 — 第二批次

> 阶段 4.2 — 2026-07-06  
> 基于全面代码分析的执行计划（78 项发现）

---

## 阶段一：🔴 HIGH 严重性 Bug 修复（6项）

| # | 文件 | 问题 | 方案 | 预估 |
|---|------|------|------|------|
| 1 | `core/module/services/module_service.py:647` | `collect_chain()` 返回值被丢弃，依赖错误静默 | 删除 `return False` 死路径（line 646-648）；或让 `collect_chain` 抛出异常 | 2min |
| 2 | `modules/customer/services.py:101-135` | `create()` 无事务，Node 孤儿风险 | `with transaction.atomic()` 包裹 create 逻辑 | 2min |
| 3 | `core/services/sample_data_service.py:30-75` | 循环内无事务，部分失败产生孤儿 | `with transaction.atomic()` 包裹整个循环 | 2min |
| 4 | `core/importexport/services/import_service.py:276-314` | 导入数据每行无事务 | `with transaction.atomic()` 包裹单行创建逻辑 | 3min |
| 5 | `core/services/china_region_service.py:197-219` | `get_tree()` N+1，数百次查询 | 用 `prefetch_related('children')` 批量预取省市县 | 5min |
| 6 | `core/models.py:172` | `User.record_failed_attempt()` 内部导入 AuthService | 移至 `AuthService`，通过信号解耦或改用 `update()` | 5min |

---

## 阶段二：🟠 MEDIUM 严重性 Bug 修复（15项）

| # | 文件 | 问题 | 方案 |
|---|------|------|------|
| 7 | `modules/calc/views.py:87-103` | JSON 格式不一致 | 使用 `json_success()` / `json_error()` |
| 8-12 | `core/views/taxonomy.py` 5处 + `core/views/settings.py` 1处 | 直接模型查询绕过 Service | 改用对应的 Service 方法 |
| 13 | `core/marketplace/services.py:93` | `except: pass` | 添加 `logger.warning` |
| 14 | `core/marketplace/services.py:143` | `except: return False` | 添加 `logger.warning` |
| 15 | `core/services/time_sync_service.py:68` | `except: return default` | 添加 `logger.warning` |
| 16 | `core/services/log_service.py:124-162` | `read_log()` 返回两种 dict 形状 | 统一为 `{"success": bool, "lines": [], ...}` |
| 17-19 | `modules/customer/services.py` | `update()` / `delete()` 缺事务 | 添加 `transaction.atomic()` |
| 20-21 | `module_service.py:669-746` | `enable_module()` / `disable_module()` 缺事务 | 添加 `transaction.atomic()` |

---

## 阶段三：🔵 模型层规范修正

| # | 文件 | 问题 | 方案 |
|---|------|------|------|
| 22 | `modules/clock/models.py` | 无注释说明占位模型意图 | 添加 docstring 注释 |
| 23-46 | `core/models.py`, `module/models.py`, `node/models.py`, `customer/models.py` | 24 处 CharField/TextField/EmailField 使用 `null=True` | 改为 `blank=True` 仅（需迁移，评估是否执行） |

---

## 阶段四：📦 封装重构（高优5项）

| # | 位置 | 方案 |
|---|------|------|
| 47 | `module_service.py:384-478` `install_module()` | 拆分 `_run_migrations`、`_verify_tables`、`_init_taxonomies` 等 |
| 48 | `core/views/api/cards.py:20-115` + `core/views/settings.py:255-288` | 提取共享的 `_get_frontpage_modules()` |
| 49 | `module_service.py:782-827` | 合并 `sync_node_type` / `sync_tool_type` → `_sync_type()` |
| 50 | `module_service.py:669-746` | 提取 `_update_type_active_status()`、`_handle_cron_tasks()` |
| 51 | `core/views/taxonomy.py` | 5 处直接查询移到 `TaxonomyService` |

---

## 阶段五：🧹 代码清理（LOW）

| # | 位置 | 操作 |
|---|------|------|
| 52 | `core/importexport/views.py:281` | 手动 POST 检查 → `@require_POST` |
| 53 | `modules/calc/views.py:79` | 同上 |
| 54 | `core/importexport/views.py:423` | `json.loads()` 加 try/except |
| 55-60 | 各处死代码 | 删除未使用的函数、导入、注释块 |
