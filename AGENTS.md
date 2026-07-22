# AGENTS.md

## 用户指令响应规则

**现有模块文档：**

**重要：** 现有模块信息已移至独立文档 `docs/现有模块.md`

Agent 应在以下情况检查该文档：
- 新增功能时，确认模块类型（node/system/tool）
- 实施认证方案时，检查所有模块的认证状态
- 排查 bug 时，确认模块配置是否正确
- 新模块安装后，及时更新该文档

**注意：** AGENTS.md 不再维护模块列表，请查看 `docs/现有模块.md` 获取最新信息。

---

**Ruff 代码检查报告：**

使用 `run.sh` 维护菜单选项 6 运行 Ruff 后，报告自动保存到 `storage/reports/ruff_YYYYMMDD_HHMMSS.txt`

Agent 在以下情况应读取最新报告：
- 用户提及 "Ruff" 或 "ruff" 并要求检查 Bug 时，读取最新报告作为参考
- 被要求修复 Ruff 发现的问题时

注意：检查 Bug 时若不提及 Ruff，则不读取此报告，仅按下方 Bug 排查规范执行。

**增量 Ruff 扫描（省 token）：**
- 日常修改后首选：`git diff --name-only HEAD \| xargs ruff check`
- 仅扫描变更文件，避免全库 202 文件格式化
- 全量扫描仅在以下情况执行：
  - 用户明确要求"全面 Ruff 检查"
  - 有新的 ruff.toml 规则引入时

**⚠️ Ruff 修复注意事项：**
- **Django signal handler 的 `sender` 参数名不可修改！** Signal dispatcher 以 `receiver(sender=..., connection=...)` 关键字形式传参，`sender` 必须保持原名。若被 ruff 的 ARG 规则重命名为 `_sender`，将导致 TypeError。
- **`unsafe-fixes = false`** 必须设置在 `ruff.toml` 顶层（不在 `[lint]` 下），否则 ARG 自动重命名规则不会被阻止。
- **通用规则：修复 ARG001 时，对于以下情况必须加 `# noqa: ARG001`（禁止重命名或删除参数）：**
  - ✅ Django view 函数 — 只要使用了 `@login_required`、`@login_required_json`、`@admin_required`、`@admin_required_json`、`@require_POST` 等装饰器，`request` 参数是 Django URL 分发器按位置传入的，不可移除或重命名
  - ✅ Django signal handler — `sender` 参数是 signal dispatcher 以关键字 `sender=` 传入的，不可重命名
  - ✅ 任何由框架按签名自动传参的函数参数（如中间件、上下文处理器等）
  - ❌ 反之，非框架调用的普通函数中未使用的参数，应直接删除参数（不设 noqa）

---

## 会话启动检查清单

每次新会话开始时，依次完成以下检查：

1. 读取 `docs/开发规范.md`，了解最新开发规范
2. 如涉及模板修改，查阅 `docs/技术规范/A04_模板开发规范.md`
3. 如涉及服务层/视图层/模型层修改，查阅对应的 B 系列技术规范
4. 不确定读哪个文档时，查阅 `docs/阅读指南.md`

---

## 开发规范

**⚠️ 模板引擎：Jinja2**
- 项目使用 **Jinja2** 模板引擎，**不使用 Django 模板语法**
- 禁止使用 `{% include "..." with ... %}`（Django 语法），应使用 `{% set var = value %}{% include "..." %}`
- 禁止使用 `{% csrf_token %}`、`{% load %}`、`{% blocktrans %}` 等 Django 专属标签
- 模板中使用 `url('namespace:name', arg)` 生成链接，详见 `A04_模板开发规范`
- 编写/修改模板前，请查阅 `docs/技术规范/A04_模板开发规范.md`

**虚拟环境：**
- Django 项目使用独立虚拟环境，位于项目目录 `venv/`
- 运行命令时使用项目内的虚拟环境：`./venv/bin/python` 或 `./run.sh`

**初始化流程规范：**

**重要：** 初始化流程已规范化，详见 `docs/技术规范/B06_初始化流程规范.md`

Agent 应在以下情况检查该文档：
- 修改 `init_db.py` 时，确认不跳过任何初始化步骤
- 修改服务层 `init_*()` 函数时，确认使用 `bulk_create` 和批量查询
- 修改 `module_service.py` 时，确认不使用 `subprocess` 调用 Django 命令
- 优化初始化性能时，参考文档中的性能优化规范

**性能目标：**
- 完整初始化（--with-data）：< 15秒
- 增量初始化（--incremental）：< 5秒

**进度记录（省 token）：**
- `docs/progress.md` 仅保留最近 ~300 条记录。
- 历史记录归档至 `docs/progress_archive/`。
- 超过 300 条时，手动归档最旧的月份。
- 每次完成编辑后，必须自动调用 `./venv/bin/python update_progress.py "修改内容描述"` 更新记录
- 修改内容应简洁明了，描述主要变更
- 如果一次会话中有多次修改，可以合并为一条记录
- **Bug 修复也必须更新进度**，不可遗漏

**杀进程安全规范：**
- 使用 `lsof -ti:<port>` 杀后端服务时，**必须**加 `-sTCP:LISTEN` 过滤，只杀监听端口的进程，避免误杀浏览器的 ESTABLISHED 连接
- 示例：`lsof -ti:8000 -sTCP:LISTEN | xargs -r kill -9`

**Bug 扫描并行化（省 token）：**
- 大规模 Bug 检查时，使用 `task` 工具分发 `explore` 子 agent 并行扫描各层
- 推荐划分：服务层 ✓ 视图层 ✓ 模板层 ✓ 模型层 ✓ 各分配一个 agent
- 每个 agent 只扫描负责的层级，返回问题列表，主 session 汇总修复结果
- 避免单次 session 顺序扫描全库导致上下文过度膨胀

**Bug 排查规范：**

### 🥇 前置步骤：读取 bugscan 报告（省 token）

开始手动排查前，按以下处理：

1. **检查最新报告**：`ls -t storage/reports/bugscan_*.json | head -1`
   - **有报告** → 读取 JSON，检查 `summary.total`
     - `total == 0`：检测器覆盖的 6 类模式（`datetime_now` / `jsonfield_default` / `nullbooleanfield` / `first_unchecked+returned` / `save_no_updates`）已确认全库无问题，**跳过下方对应的 grep 扩散扫描**
     - `total > 0`：按 `findings[].fix_hint` 定点修复，重新跑 `./venv/bin/python manage.py bugscan` 确认清零，再继续人工排查
   - **无报告**或报告超过 24 小时 → 运行 `./venv/bin/python manage.py bugscan` 生成新报告，再按上一步处理

2. **报告非本次生成**：运行结束后重新生成一次确保最新

进行 Bug 检查时（未提及 Ruff），按以下优先级执行：

| 层级 | 优先级 | 检查内容 |
|------|--------|----------|
| 服务层检查 | 🔴 高（默认必查） | `.first()` 返回值、外键访问、查询逻辑、datetime→timezone、并发安全、`save(update_fields=...)` |
| 视图层检查 | 🔴 高（默认必查） | `@login_required`/`@admin_required`/`@require_POST`、参数验证 |
| 模板层检查 | 🟡 中（按需） | 仅涉及模板修改时检查：Jinja2语法、csrf_token、外键None、block名称 |
| 模型层检查 | 🟡 中（按需） | 仅涉及模型修改时检查：JSONField default、ForeignKey on_delete、`__str__` |
| 配置层检查 | 🟡 中（按需） | 仅涉及配置修改时检查：环境变量名、APP_DIRS、WAL模式 |

**同类问题扩散扫描（防遗漏）：**
- 发现一个 Bug 后，必须用 `grep` 在全库搜索**同类模式**，确认问题是否在其他位置重复存在
- 报告必须注明"全库搜索确认：共 X 处相同模式，已修复 / Y 处为误报"
- 常见扩散扫描清单：

  | 发现的问题 | 扩散搜索命令 |
  |------------|-------------|
  | `except: pass` | `grep -rn "except.*:\s*pass" core/ modules/` |
  | `.first()` 未检查 None | `grep -rn "\.first()" core/ modules/` 逐处审查 |
  | `@login_required` 缺失 | 遍历所有视图函数核对装饰器 |
  | JSONField `default={}` | `grep -rn "JSONField.*default={" core/ modules/` |
  | `datetime.now()` | `grep -rn "datetime\.now()" core/ modules/` |
  | 模板 `csrf_token` 缺失 | 遍历所有 POST 表单 |
  | `save()` 无 `update_fields` | `grep -rn "\.save()" core/ modules/ \| grep -v "update_fields"` |
  | 静默 `except Exception` | `manage.py check` 输出中 CIMF_W007 告警 |
  | 并发无锁 | `grep -rn "threading\.Lock\|select_for_update" core/ modules/` |

**代码快照（省 token）：**
- 项目维护了分层快照：
  - `docs/snapshot_快速参考.md`（~40 行）— 模型/服务类索引，默认读取
  - `docs/snapshot_完整.md`（~400 行）— 字段详情、方法签名、遗留问题
  - `docs/模块快照/*.md` — 各模块专用快照（~10-40 行/个）
- 非全量分析时：先读快速参考，需要字段详情时读完整版，只改某模块时还读该模块快照
- 快照在每次大规模重构/分析后更新

**规范阅读规则（省 token）：**
以下规范已拆分为快速版（~200-300 行）和补充材料（含完整示例）：
- `A05_Python代码开发规范.md`（含补充材料 `A05_补充材料.md`）
- `A02_模块技术规范.md`（含补充材料 `A02_补充材料.md`）
- `A04_模板开发规范.md`（含补充材料 `A04_补充材料.md`）
- `A08_Bug排查技术规范.md`（含补充材料 `A08_补充材料.md`）

默认读快速版，看不懂规则时再读补充材料。具体映射见 `docs/阅读指南.md`。

**开发阶段高频反模式自查清单：**

新增/修改代码后，对照以下清单逐项检查，避免 4 轮 Bug 修复中发现的常见问题：

| # | 检查项 | 对应历史 Bug |
|---|--------|-------------|
| 1 | **`.first()` 结果是否检查 None？** — 使用 `obj = QuerySet.first()` 后必须判断 `if obj is None` | P0 export_filter |
| 2 | **`except:` 是否无声吞异常？** — 必须 `logger.error(...)` 或 `# noqa: S110` 注明意图 | P1 多处 S110 |
| 3 | **`mark_safe` / `|safe` / `autoescape=false` 是否必要？** — 优先用 `html.escape()` 转义用户数据后再 `mark_safe` | P1 region_select XSS |
| 4 | **模板 block 名是否与 base 一致？** — `{% block content %}` 名必须匹配 base 模板定义的 block | P2 模板不匹配 |
| 5 | **模板 POST 表单是否有 `csrf_token`？** — Jinja2: `{{ csrf_input }}` | P2 |
| 6 | **外键访问是否可能 None？** — `obj.fk_field.name` → 先 `if obj.fk_field_id` | P1 模板外键 |
| 7 | **邮件/CSV 输出是否 sanitize 用户输入？** — subject 去换行、CSV `sanitize=True` | P1 邮件注入、P2 CSV 注入 |
| 8 | **生产安全配置是否补全？** — 发布前跑 `check --deploy`（菜单选项 7） | P1 settings 配置缺失 |
| 9 | **调用 `subprocess` 是否传入可控参数？** — 固定命令列表（非字符串拼接 shell=True） | S603 |
| 10 | **`datetime.now()` 是否应替换为 `timezone.now()`？** — 前者无时区信息 | 通用 |
| 11 | **`JSONField(default={})` 是否可变成共享引用？** — 全部使用 `default=dict` 或 `default=list` | 通用 |
| 12 | **`save(update_fields=[...])` 是否覆盖全部修改字段？** — 容易遗漏新增字段 | 通用 |
| 13 | **`@login_required` 是否冗余？** — `GlobalLoginRequiredMiddleware` 已默认强制登录，白名单路径例外 | P3 冗余装饰器 |
| 14 | **并发安全？** — 共享资源有无 `threading.Lock` / `select_for_update`？`CronTask.run()` 可重入？ | Round 8 |

**进度记录（省 token）：**
- `docs/progress.md` 仅保留最近 ~300 条记录。
- 历史记录归档至 `docs/progress_archive/`。
- 超过 300 条时，手动归档最旧的月份。

---

## 项目参考

### 开发阶段

**当前阶段：Stage 4**

计划文档存放位置：`docs/stage5/`

### 技术规范

**⚠️ 重要：在开发过程中，必须参考以下技术规范文档，确保代码符合项目标准。**

项目制定了详细的技术规范文档，存放于 `docs/技术规范/` 目录：

#### 通用技术规范

| 文档 | 说明 |
|------|------|
| [A01_项目概述与技术架构](./技术规范/A01_项目概述与技术架构.md) | 项目整体介绍、技术栈、字段类型系统、项目结构 |
| [A02_模块技术规范](./技术规范/A02_模块技术规范.md) | 模块的模型、服务、视图、权限控制规范 |
| [A03_省市县联动字段技术规范](./技术规范/A03_省市县联动字段技术规范.md) | 省市县三级联动字段的设计、数据模型、API、使用指南 |
| [A04_模板开发规范](./技术规范/A04_模板开发规范.md) | Jinja2 模板开发规范，包括语法、片段库、命名规范、Checklist、反模式等 |
| [A05_Python代码开发规范](./技术规范/A05_Python代码开发规范.md) | Django 后端代码开发规范，包括文件头注释、导入规范、命名规范、Model/Service/View 规范、API 设计、测试、迁移、定时任务、**字段空值处理规范**等 |
| [A08_Bug排查技术规范](./技术规范/A08_Bug排查技术规范.md) | 基于4轮20次检查的Bug模式目录、层级检查清单、根因分析、修复优先级决策树、新模块模板 |

#### core 技术规范

| 文档 | 说明 |
|------|------|
| [B01_core_models模型设计规范](./技术规范/B01_core_models模型设计规范.md) | 核心数据模型设计，包含 User、SystemSetting、Taxonomy、Node 等 12 个模型 |
| [B02_core_services服务层规范](./技术规范/B02_core_services服务层规范.md) | 服务层业务逻辑，包含 AuthService、PermissionService、UserService 等 10 个服务 |
| [B03_core_views视图层规范](./技术规范/B03_core_views视图层规范.md) | 视图层请求处理，包含认证、管理后台、词汇表、API 等 50+ 视图函数 |
| [B04_core_forms表单与验证规范](./技术规范/B04_core_forms表单与验证规范.md) | 表单与数据验证，包含 LoginForm、UserCreateForm、ProfileForm 等 9 个表单 |
| [B05_core_urls路由与模块化规范](./技术规范/B05_core_urls路由与模块化规范.md) | URL 路由配置，包含命名规范、路径分组、动态路由等 |
| [B06_初始化流程规范](./技术规范/B06_初始化流程规范.md) | 初始化流程规范 |

如有新的技术规范需要制定，请在此目录创建文档。

### 关键配置文件

| 文件 | 用途 |
|------|------|
| `core/marketplace/marketplace.json` | 模块市场模块列表 |
| `modules/*/module.py` | 模块信息配置（MODULE_INFO 字典） |
| `core/models.py` | 核心数据模型 |
| `cimf_django/settings.py` | Django 配置 |
| `run.sh` | 启动/维护脚本 |
| `core/urls.py` | URL 路由配置 |

### 预防检查体系（Pre-commit + 自定义检查）

| 检查项 | 触发时机 | 实现方式 |
|--------|----------|----------|
| Ruff DTZ (datetime 时区) | pre-commit + 手动 `ruff check` | `ruff.toml` 启用 DTZ 规则 |
| Ruff S (安全/注入) | pre-commit + 手动 | `ruff.toml` 启用带 S 的迁移文件扫描 |
| Admin N+1 检测 | `manage.py check` | `core/checks.py` CIMF_W003 |
| Signal 处理器保护检测 | `manage.py check` | `core/checks.py` CIMF_W004 |
| 表单模板上下文检测 | `manage.py check` | `core/checks.py` CIMF_W005 |
| Deploy 安全检查 | pre-commit + run.sh 选项7 | `manage.py check --deploy --fail-level WARNING` |
| 模板问题检查 | run.sh 选项8 | `manage.py check_templates` |
| 类型检查 | pre-commit | `basedpyright`（`pyrightconfig.json` 配置） |

**手动运行命令：**
```bash
./venv/bin/ruff check                                  # 全量 Ruff
./venv/bin/python manage.py check                      # Django 系统检查（含自定义）
./venv/bin/python manage.py check --deploy             # 生产安全配置检查
./venv/bin/python manage.py check_templates            # 模板问题检查
./venv/bin/basedpyright                                # 类型检查
./venv/bin/pre-commit run --all-files                  # 全部 pre-commit 检查
```
