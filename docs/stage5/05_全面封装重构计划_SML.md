# 全面封装重构计划 — S + M + L 级（33 项）

> 阶段 5 — 2026-07-09 · 代码验证后修正版（v1.1）
> 基于 Round 2 扫描分类的 33 项封装机会 + God 类拆分
>
> 变更说明：删 M7（`throttling.py:41-46` 已有守卫，不成立），余 33 项

---

## 总览

| 级别 | 项数 | 特征 | 预估总时 |
|:----:|:----:|------|:--------:|
| S | 10 | 纯常量提取/导入清理/注解，并行安全，无运行时影响 | ~10min |
| M（轻） | 15 | 单函数抽取/移动/模型增强，子任务可并行，回归风险低 | ~25min |
| M（重） | 7 | 视图层重构/中等风险逻辑改造，需逐个验证 | ~45min |
| L | 1 | God 类 `ModuleRegistryService`（737 行）拆分为 5 个服务 | ~90min |
| **合计** | **33** | | **~170min** |

---

## S 级（10 项）— 纯常量/导入清理，并行安全

| # | 文件 | 行 | 问题 | 操作 | 风险 | 预估 |
|---|------|----|------|------|:----:|:----:|
| S1 | `core/module/services/module_registry_service.py` | 475 | 重复导入 `Module`（line 17 已导入） | 删除 `from core.module.models import Module # noqa: PLC0415` | 无 | 1min |
| S2 | `core/views/api/regions.py` | 10-14 | `_require_param(..., error_message=None)` 中 `error_message` 从未被读取 | 删除该参数及 `# noqa: ARG001`，保留 `params, param_name` | 无 | 1min |
| S3 | `core/node/views.py` | 185 | `taxonomy_items_api()` 内 `from core.models import Taxonomy # noqa: PLC0415` | 提升至文件顶部 | 无 | 1min |
| S4 | `core/importexport/services/export_service.py` | 294,298 | `_get_filtered_queryset()` 内 2 个惰性 import：`ModelRegistry`、`Node` | 试着移至顶部；若循环导入则加注释 `# 惰性: 循环导入` | 无 | 1min |
| S5 | `core/views/settings.py` | 115,124 | `["manager", "leader", "employee"]` 硬编码出现 2 次 | 模块级常量 `COMMON_ROLES = ["manager", "leader", "employee"]` | 无 | 2min |
| S6 | `cimf_django/context_processors.py` | 61-86 | `active_section()` 的 URL→section 映射 dict | 移至 `core/constants.py` 作为 `URL_SECTION_MAPPING`，原处 import 引用 | 无 | 2min |
| S7 | `core/importexport/field_extractor.py` | 34-52 | `FK_TAXONOMY_MAP` 硬编码 FK→taxonomy 映射 | 确认已为模块级常量 `FieldExtractor.FK_TAXONOMY_MAP`，加注释说明用途 | 无 | 1min |
| S8 | `core/module/services/module_service.py` | 1-11 | `class ModuleService(A, B, C): pass` 无 docstring | 加 docstring 解释多继承设计：「聚合子服务」 | 无 | 1min |
| S9 | `core/views/logs.py` | 55-65 | `logs_api()` 已定义但无对应 URL 路由，仅 TODO 注释 | 升级 TODO 为 `# TODO: logs_api 未注册路由，需在 core/urls.py 中添加` | 无 | 1min |
| S10 | `run.py` | 59 | `os.system("python manage.py migrate")` 不安全 | 改用 `subprocess.run(["python", "manage.py", "migrate"], check=True)` + 异常提示 | 低 | 3min |

**验证：** 每项后 `ruff check <文件>`

---

## M 级 — 轻（15 项）

### 批次 A：共享函数抽取（5 项，~10min）

| # | 文件 | 行 | 问题 | 操作 | 兼容性 |
|---|------|----|------|------|:------:|
| M1 | `core/module/views.py` | 37-66 | `module_to_dict()` 是 `module_manage` 视图的内嵌函数，无法单独测试，增加了视图函数复杂度 | 提为模块级顶层函数 `def _module_to_dict(...)` | ✅ 签名不变 |
| M2 | `core/services/log_service.py` | 133-138, 175-180 | `read_log()` 与 `get_log_stats()` 共享相同的「检查文件存在 + safe_exec 读取」代码段 (~5 行 × 2)。**注意：** 两函数读取后处理逻辑不同 | 抽取 `_read_log_file(log_type: str) -> list[str] \| None` 返回原始行列表；调用方各自处理 | ✅ 私有方法 |
| M3 | `core/importexport/services/export_service.py:156-169` + `import_service.py:434-448` | 两处 CSV 生成：BOM 方式不一致（`\ufeff` 手动 vs `utf-8-sig` 隐式）；`import_service` 缺少 CSV 注入防护 | 抽取 `csv_response(headers, rows, filename, sanitize=True) -> HttpResponse` → `core/utils/response.py`；统一 `utf-8-sig`；注入防护默认开启。现有调用方签名兼容 | ✅ |
| M4 | `core/services/mixins.py:74-82` → `base_service.py` | `update_fields()` 是独立工具函数（非 mixin 方法），放在 mixins.py 不合适 | 移至 `BaseService.update_fields()` 类方法；更新调用方 import | ✅ |
| M5 | `core/importexport/views.py:19-48` | `_build_filter_summaries()` 是视图层辅助函数，但只使用了服务层 API，逻辑属于导出服务 | 移至 `ExportService.build_filter_summaries()` 类方法（`@classmethod`）；视图层函数删除，调用点替换 | ✅ |

### 批次 B：参数清理 + 服务增强（4 项，~10min）

| # | 文件 | 行 | 问题 | 操作 | 兼容性 |
|---|------|----|------|------|:------:|
| M6 | `core/views/health.py` | 19-27 | `_run_check()` 的 `on_error_status` 参数：`overall` 被赋值但从未被调用方读取，函数直接返回 `"ok"`/`"degraded"` 但调用方丢弃返回值 | 删除 `on_error_status` 参数及 `overall` 变量；函数体改为 `fn(); checks[name] = "ok"` + `except: checks[name] = f"error: ..."`；保持无返回值 | ✅ |
| M7 | ~~`core/throttling.py:41-46`~~ | **已删除** | `AdminRateThrottle.get_cache_key()` 已有 `is_authenticated` 守卫（line 42），不成立 | — | — |
| M8 | `core/services/auth_service.py` | 75-98 | `login()` 内部用户查找逻辑与 `authenticate()` 重复：`authenticate()`（54-72）做 `get_first(username)`+`check_password`，`login()`（77-86）也做 `get_first(username)`+`check_password` | 消除 `login()` 中的重复 `get_first` 和 `check_password`，改为复用 `authenticate()` 返回值；失败时通过 `authenticate()` 返回 `None`，失败计数统一处理 | ✅ 行为改进 |
| M9 | `core/services/settings_service.py` | 67-75 | `_convert_setting_value()` 用 `value.isdigit()` 判断整数：端口 `587` 正常，但 IP `172.0.0.1` 含点不通过；`ProxyPort: 10808` 正常。核心问题是 `try/except` 比 `isdigit` 更健壮 | 改为 `try: return int(value)` / `try: return float(value)` 模式 | ✅ |
| M10 | `core/smtp/services/smtp_service.py:282-308` + `email_service.py:333,366,403` | `get_system_url(request=None)` 接收 request 仅用于获取当前域名 fallback。更好的设计是只返回配置的 system_url，域名拼接交给调用方或中间件 | 去掉 `request` 参数；只返回 `config.get("system_url")`；`email_service.py` 3 处调用更新，域名逻辑移至调用方 | ⚠️ 签名变更 |

### 批次 C：模型/服务层增强（3 项，~10min）

| # | 文件 | 问题 | 操作 | 兼容性 |
|---|------|------|------|:------:|
| M11 | `core/module/models.py` + `calc/views.py:65`、`smtptest/views.py:23`、`core/node/views.py:31` | 3 处 `Module.objects.filter(module_type=X, is_active=True).values_list(...)` 重复模式 | `Module` 添加 `@classmethod def get_active_ids(cls, module_type: str = None) -> list[str]`；3 处调用改为 `Module.get_active_ids(ModuleType.TOOL)` | ✅ 新增方法 |
| M12 | `modules/customer/views.py:79-86` + `core/services/taxonomy_service.py` | `_load_customer_form_data()` 对 4 个 slug 分别 `get_taxonomy_by_slug` + `get_items`，4 次独立 DB 查询。`get_items_bulk([])` 方法不存在 | **前置：** 在 `TaxonomyService` 新增 `get_items_bulk(slugs: list[str]) -> dict[str, list]` 方法（接收 slug 数组，一次查询 `Taxonomy.objects.filter(slug__in=slugs).prefetch_related("items")` 返回 dict）；然后 M12 调用 | ✅ 内部实现 |
| M13 | `core/services/tasks/base.py:99-131` | `is_enabled()` / `get_interval()` 每次调用都查 DB，同一 request 内可能反复调用 | 加 `_enabled_cache: bool \| None = None` 和 `_interval_cache: int \| None = None` 实例属性；首次查 DB 后缓存，重置时清空 | ✅ 行为改进 |

### 批次 D：数据重组（3 项，~5min）

| # | 文件 | 行 | 问题 | 操作 | 兼容性 |
|---|------|----|------|------|:------:|
| M14 | `core/services/settings_service.py` | 100-158 | `SETTINGS_META` 60 行无分组注释，新增/查找耗时长 | 按前缀分组：`# === System ===` / `# === Site ===` / `# === Welcome ===` / `# === Upload ===` / `# === Session & Login ===` / `# === Audit Log ===` / `# === Watermark ===` / `# === Time Sync ===` / `# === Cron ===` / `# === SMTP ===`；每组添加 ===== 注释线 | ✅ |
| M15 | `core/module/services/module_registry_service.py` | 256-336 | `_run_migration_subprocess()` 中包含一个 30+ 行的 f-string temp_script，嵌入函数体可读性差 | 提到类常量 `MIGRATION_SCRIPT_TEMPLATE = """..."""`；函数内只做 `temp_script.format(...)` | ✅ |
| M16 | `core/smtp/services/smtp_service.py` | 282-308 | 同 M10，`get_system_url` 重构 | 同 M10 | ⚠️ 同 M10 |

---

## M 级 — 重（7 项）

### 批次 E：视图层碎片整理（4 项，~20min）

| # | 文件 | 行 | 问题 | 操作 | 风险 |
|---|------|----|------|------|:----:|
| M17 | `core/views/settings.py` | 24-90 | `system_settings()` 65 行 POST 处理包含 2 个独立逻辑：logo 上传（42-77）与设置保存（30-40, 78-81），混合在同一个 if 块 | 拆为 `_handle_logo_upload(request, settings_dict) -> HttpResponse \| None`（返回 redirect 或 None）+ `_handle_settings_save(request, settings_dict) -> HttpResponse`（always redirect）；原函数 `system_settings` 编排调用 | 🟡 |
| M18 | `modules/customer/views.py` | 56-76 | `check_customer_permission(user, node, permission_type)` 是节点权限逻辑，应属于 `PermissionService` | 新建 `PermissionService.check_node_permission(user, node, permission_type) -> (bool, str \| None)`；`modules/customer/views.py` 中 3 处调用（203, 233, 257）改为 `PermissionService.check_node_permission(...)`；原函数删除 | 🟡 |
| M19 | `core/views/taxonomy.py` | 13-53 | `_handle_taxonomy_form()`（13-35）与 `_handle_taxonomy_item_form()`（38-53）有重复的模式：取参数→空值检查→重定向。且二者自身逻辑也不复杂，抽取收益有限 | **替代方案：** 暂不抽取，此为轻度重复。改为给 `_handle_taxonomy_form` 和 `_handle_taxonomy_item_form` 加 docstring 明确责任。**如留抽取：** 抽取 `_validate_required_fields(fields: dict) -> str \| None` 共享空值验证 | 🟢 → 🟡 |
| M20 | `core/views/settings.py:44-60` + `core/importexport/views.py:287-294` | 两处文件上传验证：settings.py 验证 MIME+大小+扩展名；importexport 验证大小+扩展名（无 MIME）。检查逻辑重叠 70% | 抽取 `validate_upload(file_obj, allowed_mimes=None, max_size=None, allowed_exts=None) -> (bool, str)`；返回值 `(valid, error_msg)` 模式 | 🟢 |

### 批次 F：中等风险逻辑改造（3 项，~25min）

| # | 文件 | 行 | 问题 | 操作 | 风险 |
|---|------|----|------|------|:----:|
| M21 | `core/views/api/cards.py` | 24-118 | `api_dashboard_cards()` 95 行大函数，4 层嵌套 try，3 个独立责任：模块遍历（48-58）→ 单卡片渲染（62-100）→ 统计获取（72-85）；WhatsApp 硬编码（86-93） | 拆分为 3 个函数：`_load_active_card_modules() -> list`（模块遍历）、`_render_single_card(module, jinja2_engine) -> dict or None`（单卡片渲染）、`_collect_module_stats(module_path) -> dict`（统计获取）；WhatsApp 硬编码改为 `try: mod_module.services` 通用模式 | 🔶 |
| M22 | `core/marketplace/services.py` | 163-186 | `_read_local_version()` 用正则从 `module.py` 文本中提取 version 字段，脆弱（需要两套正则分别匹配单/双引号），且不能确保提取的值是合法的 | 改用 `importlib.import_module` 动态导入 module 的 `.module` 子模块获取 `MODULE_INFO` dict，然后直接取 `["version"]`。安全风险低（仅临时的 import `sys.modules` 清理） | 🔶 |
| M23 | `core/node/views.py` | 220-264 | `module_dispatch()` 44 行含 3 个责任：模块存在验证（222-231）、权限检查（233-235）、视图解析与调用（237-264） | 分离为：`_check_module_exists(node_type_slug)`（验证+404）、`_resolve_view(module_path, action, node_id)`（视图名称解析→返回 view callable）、`_check_action_permission(request, action)`（权限检查）；原函数保留为 3 行编排 | 🔶 |

---

## L 级（1 项）— God 类拆分 `ModuleRegistryService`（737 行）

### 现状

```
ModuleService (11 行，facade)
├── ModuleDependencyService    (86 行)  - 模块依赖解析
├── ModuleRegistryService      (737 行)  ← GOD: 28 方法 (16 public + 12 private) 5 个责任簇
└── ModuleTaxonomyService      (93 行)  - 模块分类同步
```

**封装违规：** `_load_module_info()` 被 `module_taxonomy_service.py:14` 外部调用（违反 `_` 语义）。

### 拆分方案：5 个新服务

#### L1. `ModuleScanService`（~180 行）— 模块扫描与注册

| 方法 | 来源行 | 外部调用方 | 备注 |
|------|--------|-----------|------|
| `scan_modules()` | 28 | `module/views.py:27`, `run.py:90` | 扫描 modules/ 目录 |
| `scan_register_install()` | 64 | `syncmodules.py:30`, `module/views.py:134`, `stage4_modules.py:80` | 编排扫描→注册→安装 |
| `scan_and_register_modules()` | 130 | 无外部调用 | 薄封装 |
| `load_module_info()` | 137 | 9 处外部调用 | 公开入口 |
| `_load_module_info()` → **`public`** | 141 | `module_taxonomy_service.py:14` | 改为 public 解决封装违规 |
| `register_module()` | 205 | `marketplace/views.py:89`, `run.py:94` | DB 注册 |
| `auto_register_missing()` | 572 | `apps.py:15` | 守卫式自动注册 |

**文件：** `core/module/services/module_scan_service.py`
**类属性：** 保留 `MODULES_DIR`、`_module_info_cache`

#### L2. `ModuleInstallService`（~160 行）— 模块安装与迁移

| 方法 | 来源行 | 备注 |
|------|--------|------|
| `_check_tables_exist()` | 238 | 表结构验证 |
| `_run_migration_subprocess()` | 256 | subprocess 迁移（含 `MIGRATION_SCRIPT_TEMPLATE` 常量） |
| `_install_requirements()` | 339 | pip 安装 |
| `_verify_model_tables()` | 361 | 模型表验证 |
| `install_module()` | 382 | 完整安装管线 |
| `_init_module_sample_data()` | 447 | 样本数据初始化 |
| `register_and_install()` | 461 | 组合操作 |

**⚠ 循环依赖：** `install_module()` 内部调用 `_handle_cron_tasks`（→ LifecycleService）和 `sync_node_type`（→ ScaffoldService）→ 惰性导入 `# noqa: PLC0415`

#### L3. `ModuleLifecycleService`（~100 行）— 生命周期管理

| 方法 | 来源行 | 外部调用方 |
|------|--------|-----------|
| `_handle_cron_tasks()` | 497 | 仅被 enable_module/disable_module 内部调用 |
| `_update_type_active_status()` | 510 | 仅被内部调用 |
| `enable_module()` | 528 | `module/views.py:170` |
| `disable_module()` | 551 | `module/views.py:179` |
| `cleanup_uninstalled_modules()` | 588 | 无外部调用 |

#### L4. `ModuleQueryService`（~30 行）— 模块查询

| 方法 | 来源行 | 外部调用方 |
|------|--------|-----------|
| `get_frontpage_modules()` | 474 | `settings.py:266` |
| `get_all()` | 603 | `module/views.py:26` |
| `get_installed()` | 607 | 无外部调用 |
| `get_active()` | 611 | 无外部调用 |
| `get_by_id()` | 615 | 无外部调用 |

#### L5. `ModuleScaffoldService`（~80 行）— 模块脚手架

| 方法 | 来源行 | 备注 |
|------|--------|------|
| `_sync_type()` | 619 | 通过 `load_module_info()` 获取模块信息 |
| `sync_node_type()` | 643 | 被 `install_module()` 调用 |
| `sync_tool_type()` | 647 | 被 `install_module()` 调用 |
| `create_module()` | 651 | 脚手架生成，`module/views.py:211` |

**⚠️ 依赖：** `_sync_type()` 内部调用 `load_module_info()` — 通过 `ModuleService` 继承链访问（无需额外依赖注入，因为 `ModuleScaffoldService` 最终与 `ModuleScanService` 同属 `ModuleService` MRO）

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
    """继承聚合 7 个子服务，通过 MRO 暴露统一接口。"""
    pass
```

### 拆分步骤

```
L-a: 创建 5 个文件，复制方法体，添加独立 import     ~30min
L-b: ModuleRegistryService 中方法改为委托到新服务    ~20min
L-c: 更新 ModuleService 继承链                      ~10min
L-d: git grep "ModuleRegistryService\." 全库验证     ~5min
L-e: manage.py check + ruff check                 ~10min
L-f: python -c 验证导入                             ~5min
                                                    ~90min
```

---

## 执行顺序

```
S 批次 (10项, 并行 → ruff check)                     ~10min
  ↓
M轻 批次A (5项, 并行 → ruff check)                   ~10min
M轻 批次B (4项, 并行 → ruff check)                   ~10min
M轻 批次C (3项, 并行 → ruff check)                   ~10min
M轻 批次D (3项, 并行 → ruff check)                    ~5min
  ↓
M重 批次E (4项, 按序 → ruff check)                   ~20min
M重 批次F (3项, 按序 → ruff check)                   ~25min
  ↓
L  God类拆分 (6 子步骤)                              ~90min
  ↓
最终验证: ruff check + manage.py check               ~5min
```

---

## 验证策略

| 阶段 | 命令 |
|------|------|
| 每 S 项后 | `ruff check <文件>` |
| 每 M 轻批次后 | `git diff --name-only HEAD \| xargs ruff check` |
| 每 M 重项后 | `ruff check <文件>` + `./venv/bin/python manage.py check` |
| L-a~L-c 间 | `./venv/bin/python -c "from core.module.services.module_service import ModuleService"` |
| L-d | `git grep -n 'ModuleRegistryService\\.' core/ modules/ --include='*.py'` |
| L 级完成 | `ruff check core/module/services/` + `manage.py check` |
| 最终验证 | `ruff check` + `./venv/bin/python manage.py check` |

---

## 风险矩阵

| 风险项 | 级别 | 缓解措施 |
|--------|:----:|---------|
| `_load_module_info` 私密→public 导致外部调用扩散 | 🔴 | 改为 `load_module_info_cache()` 明确命名，`ModuleTaxonomyService` 同步更新调用 |
| `install_module()` 跨 3 个服务调用 | 🔴 | 惰性导入 (`# noqa: PLC0415`) |
| `_run_migration_subprocess` subprocess 可能失败 | 🟡 | 已有 try/except，返回格式不变 |
| `ModuleService` 继承链 7 基类 MRO 冲突 | 🟡 | Python C3 线性化，无同名方法冲突 |
| 方法遗漏改名 | 🟡 | L-d `git grep` 全库验证 |
| M22 正则→AST 替换引入安全性问题 | 🟡 | 限制 `import_module` 路径为 `modules.{id}.module`，不支持任意导入 |
| CSV 抽取后 `import_service` sanitize 行为变 | 🟡 | `generate_error_csv` 传 `sanitize=False` 保持原行为 |

---

## 回滚方案

每批次完成后 `git add -A && git commit -m "SML: <批次>"`，任一步出错可 `git checkout -- <文件>` 或 `git reset --hard`。

---

*计划版本：1.1 | 创建日期：2026-07-09 | 修正确认：路径修正、M7 删除、M8/M12 描述更新、M19 替换方案 | 计划状态：待执行*