# 全面封装重构计划 — S + M + L 级（34 项）

> 阶段 5 — 2026-07-09
> 基于 Round 2 扫描分类的 34 项封装机会 + God 类拆分

---

## 总览

| 级别 | 项数 | 特征 | 预估总时 |
|:----:|:----:|------|:--------:|
| S | 10 | 纯常量提取/导入清理/注解，并行安全，无运行时影响 | ~10min |
| M（轻） | 16 | 单函数抽取/移动/模型增强，子任务可并行，回归风险低 | ~25min |
| M（重） | 7 | 视图层重构/中等风险逻辑改造，需逐个验证 | ~45min |
| L | 1 | God 类 `ModuleRegistryService` 拆分为 5 个服务（737→~850 行） | ~90min |
| **合计** | **34** | | **~170min** |

---

## S 级（10 项）— 纯常量/导入清理，并行安全

| # | 文件 | 行 | 操作 | 风险 | 预估 |
|---|------|----|------|:----:|:----:|
| S1 | `core/module/services/module_registry_service.py` | 474 | 删除冗余 `from core.module.models import Module`（已在文件顶部导入） | 无 | 1min |
| S2 | `core/views/api/regions.py` | 10-14 | `_require_param(params, param_name, error_message=None)` 中 `error_message` 从未使用，删除参数及 `# noqa: ARG001` | 无 | 1min |
| S3 | `core/node/views.py` | 185 | `taxonomy_items_api()` 内 `from core.models import Taxonomy` → 移到文件顶部 | 无 | 1min |
| S4 | `core/importexport/services/export_service.py` | 309 | 函数内 import 核实：可移至顶层则移，需惰性则加注释 | 无 | 1min |
| S5 | `core/views/settings.py` | 115-119,124 | `["manager", "leader", "employee"]` 出现 2 次 → 模块级常量 `COMMON_ROLES` | 无 | 2min |
| S6 | `cimf_django/context_processors.py` | 58-90 | `active_section()` 的 URL→section 映射 dict → `core/constants.py` 常量 | 无 | 2min |
| S7 | `core/field_extractor.py` | 34-52 | FK→taxonomy 映射 dict → 模块级常量 | 无 | 2min |
| S8 | `core/module/services/module_service.py` | 1-11 | 给 `ModuleService` 多重继承 facade 加 docstring | 无 | 1min |
| S9 | `core/views/logs.py` | 55-65 | `logs_api()` TODO 升格 + `covered=False` 标记 | 无 | 1min |
| S10 | `run.py` | 59-62 | `os.system("python manage.py migrate")` → `subprocess.run([...], check=True)` | 低 | 3min |

---

## M 级 — 轻（16 项）

### 批次 A：共享函数抽取（5 项）

| # | 文件 | 行 | 操作 |
|---|------|----|------|
| M1 | `core/module/views.py` | 37-66 | `module_to_dict` 内嵌函数提为模块级别 |
| M2 | `core/services/log_service.py` | 123-193 | 抽取 `_read_log_file(log_type)` 消除重复 |
| M3 | `export_service.py` + `import_service.py` | 156-169 / 434-448 | 抽取 `csv_response()` → `core/utils/response.py` |
| M4 | `core/services/mixins.py:74-82` → `base_service.py` | 74-82 | `update_fields()` 移至 `BaseService` |
| M5 | `core/importexport/views.py:19-48` | 19-48 | `_build_filter_summaries()` → `ExportService.build_filter_summaries()` |

### 批次 B：参数/守卫清理 + 服务增强（5 项）

| # | 文件 | 行 | 操作 |
|---|------|----|------|
| M6 | `core/views/health.py` | 19-27 | 修复 `_run_check()` 未使用参数 |
| M7 | `core/throttling.py` | 41-46 | `AdminRateThrottle.get_cache_key()` 加 `is_authenticated` 守卫 |
| M8 | `core/services/auth_service.py` | 55-56 | `login()` 合并 `authenticate` + `login`，消除重复 lookup |
| M9 | `core/services/settings_service.py` | 67-75 | `_convert_setting_value()` 用 try/except 替换 `.isdigit()` |
| M10 | `core/smtp/services.py` | 282-308 | `get_system_url()` 改为接收 URL 字符串而非 request |

### 批次 C：模型/服务增强（3 项）

| # | 文件 | 操作 |
|---|------|------|
| M11 | `core/module/models.py` + views | 添加 `Module.get_active_ids(module_type)` 类方法，替换多处重复过滤 |
| M12 | `modules/customer/views.py:79-86` | 4 次单查询 → `TaxonomyService.get_items_bulk()` |
| M13 | `core/services/tasks/base.py:98-131` | `is_enabled()`/`get_interval()` 加实例级缓存 |

### 批次 D：数据重组（3 项）

| # | 文件 | 行 | 操作 |
|---|------|----|------|
| M14 | `core/services/settings_service.py` | 100-158 | `SETTINGS_META` 按前缀分组 + 注释 |
| M15 | `module_registry_service.py` | 256-336 | `_run_migration_subprocess()` 的 f-string 模板提为类常量 |
| M16 | `core/smtp/services.py` | 282-308 | 同 M10 |

---

## M 级 — 重（7 项）

| # | 文件 | 行 | 操作 | 风险 |
|---|------|----|------|:----:|
| M17 | `core/views/settings.py` | 24-90 | `system_settings()` POST 拆为 `_handle_logo_upload()` + `_handle_settings_save()` | 🟡 |
| M18 | `modules/customer/views.py` | 56-76 | `check_customer_permission()` → `PermissionService.check_node_permission()` | 🟡 |
| M19 | `core/views/taxonomy.py` | 13-53 | 抽取 `_handle_simple_form()` 消除重复 POST 处理 | 🟡 |
| M20 | `settings.py:44-60` + `importexport/views.py:287-294` | — | 抽取 `validate_upload()` → `core/utils/validation.py` | 🟢 |
| M21 | `core/views/api/cards.py` | 24-118 | 拆分为 3 个辅助函数；WhatsApp 硬编码→回调 | 🔶 |
| M22 | `core/marketplace/services.py` | 163-186 | `ast.literal_eval` + `import_module` 替换正则解析 | 🔶 |
| M23 | `core/node/views.py` | 220-264 | `module_dispatch()` 分离为 `_resolve_view()` + `_check_permission()` | 🔶 |

---

## L 级（1 项）— God 类拆分 `ModuleRegistryService`（737 行）

### 拆分为 5 个服务

#### L1. `ModuleScanService`（~180 行）— 扫描与注册

迁移：`scan_modules`, `scan_register_install`, `scan_and_register_modules`, `load_module_info`, `_load_module_info`（→ public），`register_module`, `auto_register_missing`

#### L2. `ModuleInstallService`（~160 行）— 安装与迁移

迁移：`_check_tables_exist`, `_run_migration_subprocess`, `_install_requirements`, `_verify_model_tables`, `install_module`, `_init_module_sample_data`, `register_and_install`

#### L3. `ModuleLifecycleService`（~100 行）— 生命周期管理

迁移：`_handle_cron_tasks`, `_update_type_active_status`, `enable_module`, `disable_module`, `cleanup_uninstalled_modules`

#### L4. `ModuleQueryService`（~30 行）— 查询

迁移：`get_frontpage_modules`, `get_all`, `get_installed`, `get_active`, `get_by_id`

#### L5. `ModuleScaffoldService`（~80 行）— 脚手架

迁移：`_sync_type`, `sync_node_type`, `sync_tool_type`, `create_module`

### 更新 Facade

```python
class ModuleService(
    ModuleDependencyService,
    ModuleScanService,
    ModuleInstallService,
    ModuleLifecycleService,
    ModuleQueryService,
    ModuleScaffoldService,
    ModuleTaxonomyService,
):
    """ModuleService 聚合 7 个子服务，通过多继承暴露统一接口。"""
    pass
```

---

## 执行顺序

```
S (并行 10 项 → ruff check)                        ~10min
├── M轻 批次A (5项 并行 → ruff check)              ~10min
├── M轻 批次B (5项 并行 → ruff check)              ~10min
├── M轻 批次C (3项 并行 → ruff check)              ~10min
├── M轻 批次D (3项 并行 → ruff check)               ~5min
│
├── M重 批次E (4项 按序  → ruff check)              ~20min
├── M重 批次F (3项 按序  → ruff check)              ~25min
│
└── L God类拆分
    ├── 创建 5 个新服务文件                          ~30min
    ├── 移动方法 + 更新 import                      ~20min
    ├── 更新 ModuleService facade                   ~5min
    ├── 修复循环导入 (惰性导入)                      ~20min
    ├── git grep 全库检查遗漏改名                    ~5min
    ├── manage.py check + ruff check                 ~10min
```

**总计预估：~170min**

---

## 验证策略

| 阶段 | 命令 |
|------|------|
| 每 S 项后 | `ruff check <文件>` |
| 每 M 轻批次后 | `git diff --name-only HEAD \| xargs ruff check` |
| 每 M 重项后 | `ruff check <文件>` + `manage.py check` |
| L 级中间 | `./venv/bin/python manage.py check` |
| L 级完成 | `ruff check core/module/services/` + `manage.py check` |
| 最终验证 | `ruff check` + `manage.py check` + `update_progress.py` |