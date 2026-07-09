# 全面 Bug 修复与封装重构计划 — 第四批次

> 阶段 5 — 2026-07-09
> 基于 5 路并行 Agent 扫描（42 项发现 + 60+ 封装机会）

---

## 阶段一：🔴 P0 安全/崩溃修复（3 项）

| # | 文件:行 | 问题 | 方案 | 预估 |
|---|---------|------|------|:----:|
| 1 | `modules/customer/services.py:157` | `NodeType.objects.get(slug="customer")` — `DoesNotExist` 未捕获，导入直接崩溃 | 改为 `.filter(slug="customer").first()` + None 检查 | 2min |
| 2 | `core/module/services/module_registry_service.py:248-249` | bare `except Exception: pass` 吞掉所有异常，调试困难 | 加 `logger.warning(f"检查模块表结构出错: {e}", exc_info=True)` | 2min |
| 3 | `core/module/services/module_registry_service.py:453-454` | `except (ImportError, ModuleNotFoundError): pass` 静默吞掉导入错误 | 加 `logger.debug(...)` 记录 | 1min |

---

## 阶段二：🟠 P1 功能异常修复（11 项）

| # | 文件:行 | 问题 | 方案 | 预估 |
|---|---------|------|------|:----:|
| 4 | `modules/customer/services.py:101-107` | `_generate_unique_code()` 字典序排序：`"cc9" > "cc10"`，导致 code 碰撞 | 解析数值后缀，按整数排序 | 5min |
| 5 | `modules/customer/services.py:150-164` | `import_row()` 只设了 `customer_code`，其余 10+ 字段被丢弃 | 映射所有 `data` 字段到 `CustomerFields.objects.create()` | 5min |
| 6 | `core/module/services/module_taxonomy_service.py:77,81` | 第三轮循环内每 taxonomy 额外 2 次 DB 查询（N+1） | 用已有的 `created_taxonomies` 和 `existing_items` 内存数据 | 5min |
| 7 | `core/module/services/module_registry_service.py:205-218` | `register_module()` 无条件覆盖 `install_on_init` 等用户配置 | 仅版本变化时更新 | 3min |
| 8 | `modules/customer/services.py:178` | `update_node()` 传空 `{}`，save 无意义 | 删除该无意义调用 | 1min |
| 9 | `core/views.py`（整个文件 68 行）| 与 `core/views/` 包共存，导入路径冲突风险 | 删除 `core/views.py`，错误处理引用已在 `settings.py` 指向包 | 2min |
| 10 | `core/templates/module/modules/create.html:80` | `{% block scripts %}` 缺少 `{{ super() }}`，可能丢失父模板脚本 | 添加 `{{ super() }}` | 1min |
| 11 | `core/templates/frames/frame_module.html` | `active_section` 未设置，侧栏高亮失效 | 在各继承模板中设置匹配的 `active_section` | 3min |
| 12 | `core/templates/marketplace/index.html:190` + `create.html:92` | `csrf_token_value` 嵌入内联 `<script>`，XSS 泄露风险 | 替换为 `window.FFE.getCsrfToken()` | 3min |
| 13 | `core/models.py:287-289` | `ChinaRegion.parent` FK 为 `CASCADE`，删除省份会级联删全部市区 | 改为 `PROTECT` | 2min |
| 14 | `core/services/auth_service.py:75-108` | `login()` 接收 `request` 参数（服务层不应见 request 对象） | 移除 `request` 参数，用 `_request` 前缀 | 3min |

---

## 阶段三：🟡 P2 代码质量修复（精选 10 项）

| # | 文件:行 | 问题 | 方案 | 预估 |
|---|---------|------|------|:----:|
| 15 | `core/importexport/views.py:59` 等 10 处 | `@login_required` 与 `@permission_required` 重复（后者已含前者） | 删除冗余的 `@login_required` | 3min |
| 16 | `core/views/api/time.py:33`, `marketplace/views.py:71` | 访问私有方法 `_fetch_time_from_server()` / `_check_conflict()` | 改为调用公开方法或提升为公开方法 | 3min |
| 17 | `core/module/services/module_dependency_service.py:1,5` | `import logging` + `logger` 变量未使用 | 删除未使用的导入和变量 | 1min |
| 18 | `core/services/log_service.py` | 多个方法缺少 `-> None` 返回类型注解 | 添加 `-> None` | 2min |
| 19 | `core/models.py:149-152` 等 5 个模型 | Meta 缺少 `ordering` | 添加合理的默认排序 | 5min |
| 20 | `config.env.sample:59` | 注释引用旧版 `init_command` | 更新注释 | 1min |
| 21 | `config.env.sample` | 缺少 `DJANGO_HOST`/`PORT`/`ADMIN_*`/`SMTP_PASSWORD` | 补充缺失的环境变量 | 3min |
| 22 | `core/services/base_service.py:87-89` | `get_or_none()` 是 `get_first()` 的冗余别名 | 删除 `get_or_none()` | 1min |
| 23 | `core/services/taxonomy_service.py:120-122` | `get_item()` 仅代理 `get_item_by_id()` | 删除冗余方法 | 1min |
| 24 | `modules/customer/services.py:112,169` | 重复的 `from django.db import transaction` 内部导入 | 删掉内部导入，用已有的模块级导入 | 1min |

---

## 阶段四：🔧 封装重构（精选 10 项）

| # | 位置 | 问题 | 方案 | 预估 |
|---|------|------|------|:----:|
| 25 | `modules/customer/services.py:110-207` | create()/update() 手动 20+ 字段赋值 | 用 `**data` + 白名单过滤，消除模板代码 | 10min |
| 26 | `core/views/settings.py:139-162,187-218` | `change_password` 与 `profile_settings` 密码修改逻辑重复 | 抽取 `_handle_password_change()` 共享函数 | 5min |
| 27 | `core/models.py` + `core/module/models.py` + `core/node/models.py` + `core/smtp/models.py` | 4 模型重复声明 `is_active` 字段 | 抽取 `IsActiveMixin` | 5min |
| 28 | `core/init_scripts/stage1_migrations.py:106-122` | `_has_pending_migrations()` 与 `common.py` 完全重复 | 统一到 `common.py`，删除重复 | 3min |
| 29 | `core/decorators.py:15-36` | `admin_required` 内 `@wraps` 顺序错误 | 调换 `@wraps` 到最内层 | 2min |
| 30 | `core/views/taxonomy.py:13-14` | `_get_taxonomy_or_error()` 纯包装 `get_object_or_404` | 直接调用 `get_object_or_404`，删除包装 | 2min |
| 31 | `core/views/node.py:46-48` | `node_types()` 仅 redirect，可用 `RedirectView` | 替换为 URL 配置中的 `RedirectView` | 3min |
| 32 | `core/init_scripts/stage3_users.py:108` | 环境变量名 `DJANGO_DJANGO_ALLOW_SEED_PROD` 双前缀 | 修正为 `DJANGO_ALLOW_SEED_PROD` | 1min |
| 33 | `core/views/api/cards.py:86-93` | WhatsApp 特定逻辑硬编码在通用 API | 提取为模块卡片接口回调 | 10min |
| 34 | `modules/customer/forms.py:1-228` | 每个字段手动 `attrs={"class": "form-control"}` | 使用已有的 `BootstrapFormMixin` | 10min |

---

---

## Round 2 修复（2026-07-09 追加）

| # | 严重度 | 文件 | 问题 | 修复 |
|---|--------|------|------|------|
| 35 | 🔴 P0 | `core/views/settings.py:140` | `_handle_password_change` 被 `@login_required` 装饰，但参数顺序不符，调用时崩溃 | 移除装饰器 |
| 36 | 🔴 P0 | `core/views/settings.py:150` | `change_password` 无 `@login_required`，匿名用户可访问 | 添加 `@login_required` |
| 37 | 🟠 P1 | `core/marketplace/services.py:156` | `datetime.datetime.now()` 应使用 `timezone.now()` | 替换 |
| 38 | 🟠 P1 | `core/templates/tools/tools_dashboard.html:47` | 坏 URL `core:module_manage` 不存在 → `module:list` | 修正 |
| 39 | 🟡 P2 | `core/node/services/node_type_service.py:13` | `_get_node_type_or_none` 与 `get_by_id` 完全重复 | 删除私有方法，统一使用 `get_by_id` |
| 40 | 🟡 P2 | `modules/customer/services.py:149` | `update()` 中 `allowed_fields` 与 `FIELD_MAPPING` 重复 | 复用 `FIELD_MAPPING` |

---

## 暂缓变更（不计入本次执行）

- `core/module/services/module_registry_service.py` God 类拆分（736行）— 风险大，需专项计划
- `core/importexport/services` 文件格式处理抽取 — 需上游重构稳定后
- `core/services/settings_service.py` SETTINGS_META 迁移至 JSON — 设计决策需讨论
- `core/models.py:143` `User.created_at` 与 `date_joined` 合并 — 涉及迁移，风险高
- 模板 inline CSS/JS 提取至外部文件 — 纯风格优化，与 Bug 修复无关
- 模型 `CharField/TextField null=True` 修正 — 涉及迁移，需评估影响
- `config.env.sample` 补充完整环境变量 — 文档小问题，单独处理

---

## 执行顺序

```
阶段一(P0) → 阶段二(P1) → 阶段三(P2) → 阶段四(封装)
                         ↘
                     每项修改后：ruff check 受影响文件
                     全部完成后：manage.py check
```

## 验证

1. 每项修改后增量 ruff：`git diff --name-only HEAD | xargs ruff check`
2. 全部完成后：`./venv/bin/python manage.py check`
3. 更新进度：`./venv/bin/python update_progress.py "..."`

---

*计划版本：1.0 | 创建日期：2026-07-09*
