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

**进度记录：**
- 每次完成编辑后，必须自动调用 `./venv/bin/python update_progress.py "修改内容描述"` 更新记录
- 修改内容应简洁明了，描述主要变更
- 如果一次会话中有多次修改，可以合并为一条记录
- **Bug 修复也必须更新进度**，不可遗漏

**杀进程安全规范：**
- 使用 `lsof -ti:<port>` 杀后端服务时，**必须**加 `-sTCP:LISTEN` 过滤，只杀监听端口的进程，避免误杀浏览器的 ESTABLISHED 连接
- 示例：`lsof -ti:8000 -sTCP:LISTEN | xargs -r kill -9`

**Bug 排查规范：**

进行 Bug 检查时（未提及 Ruff），仅按 A08 规范执行系统化检查，不读取 ruff 报告：

| 层级 | 优先级 | 检查内容 |
|------|--------|----------|
| 服务层检查 | 🔴 高 | `.first()` 返回值、外键访问、查询逻辑、datetime→timezone |
| 视图层检查 | 🔴 高 | `@login_required`/`@admin_required`/`@require_POST`、参数验证 |
| 模板层检查 | 🟡 中 | Jinja2语法、csrf_token、外键None、block名称 |
| 模型层检查 | 🟡 中 | JSONField default、ForeignKey on_delete、`__str__` |
| 配置层检查 | 🟡 中 | 环境变量名、APP_DIRS、WAL模式 |

---

## 项目参考

### 开发阶段

**当前阶段：Stage 4**

计划文档存放位置：`docs/stage4/`

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
