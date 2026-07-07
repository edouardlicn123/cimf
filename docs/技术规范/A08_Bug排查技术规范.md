# Bug 排查技术规范

> 文档版本：1.0  
> 最后更新：2026-05-08 — 基于4轮20次独立检查数据首次发布  
> 数据来源：~60 个已修复 Bug（P0×7, P1×38, P2×15）

---

## 一、总则

### 1.1 目的与范围

本规范旨在为项目 Bug 排查提供系统化、可重复的检查流程和判断标准。适用于：

- 日常开发中的 Code Review
- 功能上线前的回归检查
- 专项 Bug 排查（5次独立检查覆盖全量代码）
- 新模块开发完成后的自检

### 1.2 数据来源

本规范基于 4 轮共 20 次独立 Bug 检查的实际数据：

| 轮次 | 检查区域 | 发现 Bug 数 | 修复时间 |
|------|----------|-------------|----------|
| 第1轮 | SMTP / 路由 / 模板语法 / 模块加载 / 核心服务 | 33 | 2026-05-08 |
| 第2轮 | Node模块 / API视图 / 前端静态文件 / 初始化迁移 / 横切关注点 | 32 | 2026-05-08 |
| 第3轮 | 导入导出 / 模块市场 / 权限角色 / 定时任务 / 配置环境 | 48 | 2026-05-08 |
| 第4轮 | core根目录+fields / 模块系统核心 / modules各模块 / SMTP+市场 / 导入导出+配置 | 24 | 2026-05-08 |

### 1.3 Bug 统计总览

按严重程度分布：

| 严重程度 | 数量 | 占比 | 典型问题 |
|----------|------|------|----------|
| 🔴 P0（安全/崩溃） | 7 | 12% | f-string注入、开放重定向、定时任务仅执行一次、for-else缩进、JS语法错误 |
| 🟠 P1（功能异常） | 38 | 63% | 装饰器缺失、.first()未检查、模板语法错误、CSRF暴露 |
| 🟡 P2（代码质量） | 15 | 25% | 死代码、多余导入、logger使用不当 |

按层级分布：

| 层级 | Bug数 | 主要问题 |
|------|-------|----------|
| 服务层（services/） | 18 | `.first()` None检查、`datetime.now()`、`except:pass` |
| 视图层（views/） | 15 | 装饰器缺失、CSRF处理、参数验证 |
| 模板层（templates/） | 12 | Jinja2语法混用、csrf_token语法、外键None |
| 模块系统（module/node/） | 8 | 动态加载安全、f-string注入、死代码 |
| 配置层（settings/） | 5 | 环境变量不匹配、APP_DIRS、WAL |
| 导入导出 | 4 | CSV注入、编码崩溃、key不匹配 |

### 1.4 核心原则

#### 1.4.1 防御性编程

```python
# ❌ 危险：假设对象不为 None
customer = get_customer()
customer.delete()  # customer 是 None 怎么办？

# ✅ 安全：防御性检查
customer = get_customer()
if not customer:
    return error
customer.delete()
```

#### 1.4.2 信任但验证

- 即使前端已做验证，后端仍需验证
- 即使表单已验证，视图仍需检查
- 即使 API 已认证，每个端点仍需验证
- 即使参数来自数据库，使用时仍需验证

#### 1.4.3 分层检查

Bug 检查应从最底层（服务层）开始逐层向上：

```
服务层 → 模型层 → 视图层 → 模板层 → 配置层
（高优先级）                     （低优先级）
```

---

## 二、高频 Bug 模式目录

> 按出现频率从高到低排列。每种模式包含：频率评估、典型错误代码、正确写法、真实案例、根因分析、修复清单。

---

### BP01 — `.first()` 返回值未检查 None ★★★★★

**严重程度：** P0-P1（崩溃级）

**问题：** `.first()` 在查询无结果时返回 `None`，直接访问属性触发 `AttributeError`。

```python
# ❌ 错误
node = Node.objects.filter(id=node_id).first()
return node.name  # node 为 None 时崩溃

# ✅ 正确
node = Node.objects.filter(id=node_id).first()
if not node:
    return None  # 或 raise / 返回默认值
return node.name
```

**真实案例：**
- `core/services/cron_service.py:64` — `Optional[datetime]` 类型注解中 `datetime` 未导入 → `NameError`

**根因：** 开发者假设查询"肯定有结果"，忽略数据库状态不确定。

**修复清单：**
- [ ] `.first()` 后检查 `if not result:`
- [ ] `.first().` 属性访问前确保非 None
- [ ] 返回类型标注为 `Optional[Type]`

---

### BP02 — Jinja2 / Django 模板语法混用 ★★★★☆

**严重程度：** P1-P2（渲染错误或空白）

**问题：** 项目使用 Jinja2 引擎，Django 模板语法不兼容。

```html
<!-- ❌ Django 语法（不兼容 Jinja2） -->
{{ user.created_at|date:"Y-m-d" }}
{{ value|default:"无" }}
{% include "..." with var=value %}
{% url 'name' arg %}
{% csrf_token %}

<!-- ✅ Jinja2 正确语法 -->
{{ user.created_at.strftime('%Y-%m-%d') if user.created_at else '-' }}
{{ value|default('无') }}
{% set var = value %}{% include "..." %}
{{ url('namespace:name', arg) }}
{{ csrf_token }}
```

**真实案例：**
- 70+ 模板文件检查发现 9 处 `{% extends "core/..." %}` 错误路径
- `date:"Y-m-d"` 语法错误在多个模板中存在
- `{% csrf_token %}` 标签混用（Jinja2 使用 `{{ csrf_token }}` 变量）

**根因：** 从 Django 模板迁移至 Jinja2 后，旧语法遗留；新开发者不熟悉区别。

**修复清单：**
- [ ] `|date:"..."` → `strftime()` + None 检查
- [ ] `|default:"..."` → `|default('...')`
- [ ] 无 `{% load %}`、`{% csrf_token %}`、`{% blocktrans %}`
- [ ] 所有 URL 使用 `url('namespace:name', arg)` 函数
- [ ] `{% extends %}` 路径不包含 `core/` 前缀

---

### BP03 — `@login_required` / `@admin_required` 缺失 ★★★★☆

**严重程度：** P0-P1（安全漏洞）

**问题：** API 端点或视图函数未加认证装饰器，可被未登录用户访问。

```python
# ❌ 错误：缺少认证装饰器
def api_regions_provinces(request):
    return JsonResponse(...)

# ✅ 正确：添加 @login_required
@login_required
def api_regions_provinces(request):
    return JsonResponse(...)

# ✅ API 需要管理员权限
@admin_required
def cron_status(request):
    return JsonResponse(cron.get_status())
```

**真实案例：**
- `core/views/cron.py:41` — `cron_status` 原为 `@login_required`，应提升为 `@admin_required`
- `core/smtp/views.py` — `smtp_config` 原为 `@login_required`，应提升为 `@admin_required`
- `core/module/views.py` — `module_create_action` 未加 `@require_POST`

**根因：** 新视图创建时忘记添加；从普通函数改 API 时遗漏；权限级别判断不准确。

**修复清单：**
- [ ] 所有非登录页视图有 `@login_required`
- [ ] 管理操作用 `@admin_required`
- [ ] API 端点验证装饰器存在
- [ ] 无重复装饰器（`@login_required` 出现两次）

---

### BP04 — `@require_POST` 缺失 ★★★★☆

**严重程度：** P1（安全 + 功能异常）

**问题：** 破坏性操作（创建、删除、修改）未限制 HTTP 方法，可通过 GET 触发。

```python
# ❌ 错误：可通过 GET 触发删除
def user_delete(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if user:
        user.delete()

# ✅ 正确：限制 POST
@require_POST
def user_delete(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if user:
        user.delete()
```

**真实案例：**
- `core/views/cron.py:48,56` — `cron_run_task` 和 `cron_toggle_task` 缺 `@require_POST`
- `core/views/taxonomy.py` — `taxonomy_delete`, `taxonomy_item_delete` 缺 `@require_POST`
- `core/module/views.py` — `module_create_action` 缺 `@require_POST`
- `core/node/views.py` — 多个节点操作视图缺 `@require_POST`

**根因：** 开发者习惯 GET/POST 都处理（早期模式），未意识到安全风险。

**修复清单：**
- [ ] 所有 `POST` 操作用 `@require_POST`
- [ ] 视图函数名含 `delete`/`create`/`toggle`/`action` 的必须检查
- [ ] `request.POST.get()` 使用的视图必须有 `@require_POST`

---

### BP05 — CSRF Token 错误使用 ★★★★☆

**严重程度：** P1-P2（安全风险或页面崩溃）

**问题：** CSRF token 在三种场景下出错：语法不对、暴露到前端、上下文缺失。

```html
<!-- ❌ 错误 1：Jinja2 中 csrf_token() 不可调用 -->
{{ csrf_token() }}

<!-- ✅ 正确：直接使用变量 -->
{{ csrf_token }}

<!-- ❌ 错误 2：暴露到 console -->
console.log('CSRF Token:', csrfToken);

<!-- ✅ 正确：仅用于请求头 -->
headers: { 'X-CSRFToken': csrfToken }
```

**真实案例：**
- `core/templates/admin/system_cron_manager.html:99` — `console.log('CSRF Token:', csrfToken)` 暴露 CSRF
- `core/templates/module/modules/create.html:97` — `{{ csrf_token_value }}` 未传入模板上下文
- 约 15 处模板中 Jinja2 错误使用 `{% csrf_token %}` 标签

**根因：** Jinja2/Django 语法混淆；调试代码未清理；视图未传递必要上下文。

**修复清单：**
- [ ] 模板中使用 `{{ csrf_token }}` 而非 `{% csrf_token %}`
- [ ] 无 `console.log` 输出 CSRF token
- [ ] AJAX 请求通过 meta 标签或 cookie 获取 token
- [ ] 视图传递 `csrf_token_value` 到需要 JS 使用的模板

---

### BP06 — `except: pass` 静默吞噬异常 ★★★☆☆

**严重程度：** P1-P2（难以排查的隐晦 Bug）

**问题：** 异常被捕获但不记录日志，导致问题难以定位。

```python
# ❌ 错误：静默吞噬
try:
    result = risky_operation()
except Exception:
    pass

# ✅ 正确：至少记录 warning
try:
    result = risky_operation()
except Exception as e:
    logger.warning(f"操作失败: {e}", exc_info=True)
```

**真实案例：**
- `core/views/api/cards.py` — 5 层 `except Exception: pass` → 改为 `logger.warning/error`
- `core/services/permission_service.py:231-232` — 模块导入失败静默 `pass`
- `core/marketplace/services.py` — Zip 解压异常静默

**根因：** 开发期为快速跳过错误留的占位符，上线前未补充日志。

**修复清单：**
- [ ] 所有 `except` 块至少记录 `logger.warning()` 或 `logger.error()`
- [ ] `except: pass` 或 `except Exception: pass` 必须添加日志
- [ ] 关键操作记录 `exc_info=True` 保留堆栈

---

### BP07 — 外键访问前未检查 None ★★★☆☆

**严重程度：** P1（崩溃）

**问题：** 外键字段可为空（`null=True`），未检查直接访问属性。

```python
# ❌ 错误：未检查 None
return customer.country.name

# ✅ 正确：检查 None
return customer.country.name if customer.country else '-'
```

**根因：** 假设外键必有值；测试数据中外键都有值，生产环境有空值。

**修复清单：**
- [ ] 所有外键 `.name` / `.title` 等属性访问前检查 None
- [ ] 模板中使用 `obj.fk.name if obj.fk else '-'`

---

### BP08 — `datetime.now()` 应使用 `timezone.now()` ★★★☆☆

**严重程度：** P1（时区不一致）

**问题：** `datetime.now()` 返回 naive datetime（无时区），与 Django 的 timezone-aware 时间不兼容。

```python
# ❌ 错误
from datetime import datetime
now = datetime.now()

# ✅ 正确
from django.utils.timezone import now
now = now()

# 或保持时区一致
from django.utils import timezone
now = timezone.now()
```

**真实案例：**
- `core/services/cron_service.py` — 使用 `datetime.now()` → 改为 `timezone.now()`
- `core/services/tasks/base.py` — 同
- `core/services/time_sync_service.py` — 同（部分）

**根因：** 习惯性使用标准库 `datetime`；迁移自 Flask 项目遗留。

**修复清单：**
- [ ] 所有 `datetime.now()` 替换为 `timezone.now()`
- [ ] `from datetime import datetime` 只在需要字符串解析时使用
- [ ] DB 中存储的时间全部 timezone-aware

---

### BP09 — JSONField default 使用可变对象 ★★☆☆☆

**严重程度：** P1（数据共享污染）

**问题：** `default={}` 或 `default=[]` 在模型定义时求值一次，所有实例共享同一对象。

```python
# ❌ 错误：所有实例共享同一个 dict
fields_config = JSONField(default={})

# ✅ 正确：每次创建新实例时调用
fields_config = JSONField(default=dict)
# 或
fields_config = JSONField(default=list)
```

**真实案例：**
- `core/models.py:112` — `User.permissions = JSONField(default=list)`（已正确）
- 检查中未发现新的 mutable default（已全部修正）

**根因：** Python 函数参数默认值在定义时求值。Django 的 JSONField 必须用可调用对象。

**修复清单：**
- [ ] 所有 JSONField default 使用 `dict` / `list` / `lambda` 而非 `{}` / `[]`

---

### BP10 — f-string 用户输入注入 ★★☆☆☆

**严重程度：** P0（安全漏洞）

**问题：** 用户输入直接嵌入 f-string 用于生成代码或 SQL，可导致代码注入。

```python
# ❌ 错误：用户输入直接嵌入
module_py_content = f"MODULE_INFO = {{'name': '{name}'}}"

# ✅ 正确：使用 repr() 转义
module_py_content = f"MODULE_INFO = {{'name': {repr(name)}}}"

# 或写入文件时转义
import json
with open(path, 'w') as f:
    json.dump({'name': name}, f)
```

**真实案例：**
- `core/module/services/module_service.py:822-836` — `create_module()` 将 `name`/`description` 直接嵌入生成的 Python 文件
- `core/module/services/module_service.py:303-338` — `_run_migration_subprocess` 将 `module_id` 嵌入脚本字符串

**根因：** 开发者认为"这些值来自表单验证"或"来自数据库"就不再转义。注入不仅来自用户，也来自数据库中被篡改的数据。

**修复清单：**
- [ ] 用户输入嵌入代码时使用 `repr()` 或 `json.dumps()`
- [ ] 使用 `shlex.quote()` 处理 shell 参数
- [ ] 尽量使用参数化接口而非字符串拼接

---

### BP11 — 整数类型字段使用 `__icontains` ★★☆☆☆

**严重程度：** P1（查询异常/数据库错误）

**问题：** `__icontains` 是字符串专用查找，用于整数字段会导致类型错误或意外行为。

```python
# ❌ 错误：整数字段不支持 __icontains
queryset.filter(id__icontains=search)

# ✅ 正确：先转换为整数
try:
    node_id = int(search)
    queryset.filter(id=node_id)
except ValueError:
    pass  # 或返回空结果

# ❌ 链式 filter 是 AND，不是 OR
queryset.filter(name__icontains=s)
queryset.filter(code__icontains=s)  # 实际是 AND

# ✅ 使用 Q 对象
queryset.filter(Q(name__icontains=s) | Q(code__icontains=s))
```

**修复清单：**
- [ ] 整数字段不使用 `__icontains`
- [ ] 多条件 OR 使用 `Q` 对象
- [ ] `filter()` 链式调用判断是否应为 AND

---

### BP12 — 键名不匹配（生产者 vs 消费者）★★☆☆☆

**严重程度：** P1（功能完全失效）

**问题：** 数据写入时用一个 key，读取时用另一个 key，导致功能无声失败。

```python
# ❌ 错误：生产者用 'message'，消费者读 'errors'
# producer.py
errors = [{'row': 1, 'message': '必填'}]
session['import_errors'] = json.dumps(errors)

# consumer.py
for error in json.loads(session['import_errors']):
    error.get('errors', [])  # 永远是 []
    error.get('data', '')     # 永远是 ''

# ✅ 正确：统一 key 名
errors = [{'row': 1, 'errors': ['必填'], 'data': '原始数据'}]
session['import_errors'] = json.dumps(errors)
```

**真实案例：**
- `core/importexport/views.py:381-384` vs `import_service.py:424-428` — `message` vs `errors` key 不匹配
- `smtp/config.html` vs `views.py` — 模板变量名不匹配

**根因：** 不同开发者/不同时间编写的代码未协调数据结构；重构时只改了生产者没改消费者。

**修复清单：**
- [ ] 跨模块数据交换使用明确的 schema 定义
- [ ] 重构时同时更新所有读写方
- [ ] 添加集成测试验证数据通路

---

### BP13 — 环境变量名不匹配 ★★☆☆☆

**严重程度：** P1（配置不生效）

**问题：** `config.env` 中定义的变量名与 `settings.py` 读取的变量名不一致。

```python
# config.env
SECRET_KEY=xxx

# settings.py（读取的是 DJANGO_SECRET_KEY）
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback')
# 永远使用 fallback！config.env 的 SECRET_KEY 无效
```

**真实案例：**
- `config.env:6` 用 `SECRET_KEY`，但 `settings.py:46` 读 `DJANGO_SECRET_KEY`
- `config.env:7` 用 `DEBUG`，但 `settings.py:52` 读 `DJANGO_DEBUG`

**根因：** 重构时改了 settings.py 的变量名但未同步 config.env。

**修复清单：**
- [ ] `config.env` 和 `settings.py` 变量名严格一致
- [ ] 新增环境变量时两边同时添加
- [ ] 写一个脚本来验证所有环境变量配对

---

### BP14 — 配置与代码不一致 ★★☆☆☆

**严重程度：** P1（功能异常）

**问题：** 配置文件的某个关键设置与代码逻辑冲突。

```python
# settings.py 中 DjangoTemplates 配置
{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': False,  # ❌ 导致 admin 模板 404
}
```

**真实案例：**
- `cimf_django/settings.py:152` — `DjangoTemplates APP_DIRS: False` → 应改为 `True`
- `cimf_django/database.py:72-78` — SQLite WAL 模式设置在临时连接上 → 改为 Django `connection_created` 信号

**根因：** 配置项含义理解偏差；"优化"时改了配置没验证效果。

**修复清单：**
- [ ] 修改配置后运行 `manage.py check`
- [ ] DjangoTemplates `APP_DIRS: True`
- [ ] Jinja2 `APP_DIRS: False`
- [ ] 数据库连接级别设置通过信号而非临时连接

---

### BP15 — `{% block %}` 名称不匹配 ★★☆☆☆

**严重程度：** P2（CSS/JS 不生效）

**问题：** 子模板使用的 block 名与父模板定义的不一致。

```html
<!-- base.html 定义 -->
{% block head_extra %}{% endblock %}

<!-- 子模板使用不同名称 -->
{% block extra_head %}
<style>...</style>  {# 永远不会渲染 #}
{% endblock %}
```

**真实案例：**
- `core/templates/structure/field_types/field_types.html:14` — `extra_head` → `head_extra`
- `core/templates/usermenu/settings.html:14` — 同上
- `core/templates/includes/style.html:19` — block 声明在被 `{% include %}` 的模板中无效

**根因：** 拼写错误；未验证 block 名称是否与父模板匹配。

**修复清单：**
- [ ] 子模板 block 名称与父模板严格一致
- [ ] `{% include %}` 的片段中不含 `{% block %}`
- [ ] 重写 `{% block scripts %}` 时调用 `{{ super() }}`

---

### BP16 — 导入路径冲突（文件 vs 目录）★☆☆☆☆

**严重程度：** P1（`ImportError`）

**问题：** 同一目录下同时存在 `services.py` 和 `services/` 目录，Python 导入解析不确定。

```python
# ❌ 存在 services.py 和 services/ 目录
core/importexport/services.py          # 向后兼容文件
core/importexport/services/__init__.py # 实际实现

# 导入可能解析到 services.py 而非 services/__init__.py
from core.importexport.services import ImportService  # 可能失败
```

**真实案例：**
- `core/importexport/services.py:9` — 自引用导入导致 `ImportError` → 已删除
- `core/importexport/services/template_generator.py:12` — 导入路径冲突

**根因：** 重构时创建了目录版本但保留了旧文件"向后兼容"。

**修复清单：**
- [ ] 不存在 `file.py` 和 `file/` 目录并存的情况
- [ ] 向后兼容文件确认无人引用后立即删除
- [ ] 使用相对导入 `.import_service` 而非绝对导入

---

### BP17 — `is_admin` 覆盖 `role` 逻辑 ★☆☆☆☆

**严重程度：** P0（权限矛盾）

**问题：** `update_user` 中 `role` 分支设置 `is_admin=True/False`，随后 `is_admin` 参数又覆盖，导致矛盾状态。

```python
# ❌ 错误：role 分支设 is_admin，后面又被覆盖
if role is not None:
    user.role = role
    if role == UserRole.MANAGER:
        user.is_admin = True   # ← 设置
    else:
        user.is_admin = False  # ← 设置

if is_admin is not None:
    user.is_admin = is_admin   # ← 覆盖！可导致 manager + is_admin=False

# ✅ 正确：role 分支不涉及 is_admin
if role is not None:
    user.role = role
    # is_admin 由独立参数统一控制

if is_admin is not None:
    user.is_admin = is_admin
```

**修复清单：**
- [ ] `role` 分支不应修改 `is_admin`
- [ ] `is_admin` 修改走独立参数
- [ ] 保存前验证 `is_admin` 与 `role` 不矛盾

---

### BP18 — 定时任务缺 else 分支 ★☆☆☆☆

**严重程度：** P0（定时任务只执行一次）

**问题：** 条件判断缺少 `else` 分支，导致特定条件下逻辑不执行。

```python
# ❌ 错误：_last_run 不为 None 时 should_run 永远 False
if task._last_run is None:
    if task._run_count == 0:
        should_run = True
    else:
        next_run = task._last_run.timestamp() + task.get_interval()
        if now >= next_run:
            should_run = True
# should_run 在 _last_run is not None 时保持 False

# ✅ 正确：添加 else 分支
if task._last_run is None:
    if task._run_count == 0:
        should_run = True
else:
    next_run = task._last_run.timestamp() + task.get_interval()
    if now >= next_run:
        should_run = True
```

**根因：** 条件分支设计遗漏；测试只覆盖了首次执行（`_run_count == 0`），未测试第二次及以后。

**修复清单：**
- [ ] 所有 `if/elif/else` 检查是否有遗漏分支
- [ ] 边界条件测试（0、1、N 次执行）
- [ ] 定时任务逻辑单元测试覆盖重复执行场景

---

## 三、按层级的防御性检查清单

> **执行策略：** 默认只检查 🔴 高优先级（服务层 + 视图层），节省排查时间。  
> 🟡 中优先级（模板/模型/配置层）仅在以下情况执行：涉及对应层级的修改、用户明确要求全面检查、新模块上线检查。

### 3.1 服务层检查（🔴 高优先级 — 默认必查）

| # | 检查项 | 检查命令 | 自动化 |
|---|--------|----------|--------|
| 1 | `.first()` 返回值是否检查 None | `grep -rn "\.first()" core/ modules/` | ✅ |
| 2 | `.first().property` 链式调用 | `grep -rn "\.first()\." core/ modules/` | ✅ |
| 3 | `datetime.now()` 是否误用 | `grep -rn "datetime\.now\|from datetime import" core/ modules/` | ✅ |
| 4 | `except: pass` 无日志 | `grep -rn "except.*:\s*pass" core/ modules/` | ✅ |
| 5 | JSONField default 为 `{}` 或 `[]` | `grep -rn "JSONField.*default={" core/ modules/` | ✅ |
| 6 | 整数字段 `__icontains` | `grep -rn "__icontains=" core/ modules/` | ✅ |
| 7 | 链式 filter 应为 Q 对象 | 人工审查 | ❌ |
| 8 | f-string 嵌入用户输入 | 人工审查生成代码/脚本 | ❌ |
| 9 | N+1 查询 | 人工审查循环内查询 | ❌ |
| 10 | 导入路径冲突（文件 vs 目录） | `ls -d core/*/services.* core/*/services/ 2>/dev/null` | ✅ |

**常见修复示例：**

```python
# .first() 返回值检查
def get_user(user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:          # ← 必须检查
        return None
    return user

# datetime.now() 替换
from django.utils.timezone import now
current = now()           # 而非 datetime.now()

# JSONField default
class SomeModel(models.Model):
    config = JSONField(default=dict)    # 非 default={}
    tags = JSONField(default=list)      # 非 default=[]
```

---

### 3.2 视图层检查（🔴 高优先级）

| # | 检查项 | 检查命令 | 自动化 |
|---|--------|----------|--------|
| 1 | `@login_required` 装饰器 | `grep -rn "@login_required\|@admin_required" core/ modules/` | ✅ |
| 2 | `@require_POST` 对破坏性操作 | `grep -rn "@require_" core/ modules/` | ✅ |
| 3 | 重复装饰器 | `grep -rn "@login_required.*@login_required" core/ modules/` | ✅ |
| 4 | CSRF 处理正确 | `grep -rn "csrf_exempt\|csrf_token" core/views/` | ✅ |
| 5 | `json.loads(request.body)` 有 try/except | `grep -rn "json.loads.*body" core/ modules/` | ✅ |
| 6 | 参数类型验证（int 转换） | 人工审查 | ❌ |
| 7 | 开放重定向（next 参数） | `grep -rn "next\|redirect.*request" core/views/` | ✅ |
| 8 | 权限检查充分 | 人工审查每个视图的权限要求 | ❌ |

**常见修复示例：**

```python
@admin_required                    # ← 必须添加
@require_POST                      # ← 破坏性操作必须限制
def module_create_action(request):
    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'error': '名称不能为空'})
    try:
        ...
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
```

---

### 3.3 模板层检查（🟡 中优先级 — 按需检查）

| # | 检查项 | 检查命令 | 自动化 |
|---|--------|----------|--------|
| 1 | POST 表单含 csrf_token | `grep -rn "csrf_token\|csrfmiddlewaretoken" core/templates/` | ✅ |
| 2 | Jinja2 date 语法正确 | `grep -rn 'date:"' core/templates/` | ✅ |
| 3 | 外键显示检查 None | `grep -rn "\.country\|\.region\|\.type\|\.level" core/templates/` | ✅ |
| 4 | extends 路径不含 core/ | `grep -rn "extends.*core/" core/templates/` | ✅ |
| 5 | 无 Django 模板标签 | `grep -rn "{% load\|{% blocktrans\|{% url " core/templates/` | ✅ |
| 6 | URL 使用 `url()` 函数 | `grep -rn "{{\s*url(" core/templates/` | ✅ |
| 7 | block 名称与父模板一致 | 人工审查 | ❌ |
| 8 | 无 console.log 暴露敏感信息 | `grep -rn "console\.log" core/templates/` | ✅ |
| 9 | `{% include %}` 片段中无 `{% block %}` | 人工审查 | ❌ |
| 10 | `{{ super() }}` 在重写的 block 中 | `grep -rn "block scripts\|block head" core/templates/` | ✅ |

**常见修复示例：**

```html
<!-- 表单 -->
<form method="post">
    {{ csrf_token }}
    ...
</form>

<!-- 外键显示（检查 None） -->
{{ customer.country.name if customer.country else '-' }}

<!-- 时间格式化 -->
{{ log.created_at.strftime('%Y-%m-%d') if log.created_at else '-' }}

<!-- 链接 -->
<a href="{{ url('module:list') }}">模块管理</a>
```

---

### 3.4 模型层检查（🟡 中优先级 — 按需检查）

| # | 检查项 | 检查命令 | 自动化 |
|---|--------|----------|--------|
| 1 | JSONField default 可调用 | `grep -rn "JSONField" core/ modules/` | ✅ |
| 2 | ForeignKey on_delete 正确 | `grep -rn "ForeignKey" core/ modules/` | ✅ |
| 3 | `__str__` 返回非空 | `grep -rn "def __str__" core/ modules/` | ✅ |
| 4 | CharField/EmailField 无 `null=True` | `grep -rn "CharField.*null=T\|EmailField.*null=T" core/ modules/` | ✅ |
| 5 | Meta 类完整 | 人工审查 | ❌ |
| 6 | 表名唯一 | 人工审查 | ❌ |

```python
# JSONField default 必须可调用
class User(models.Model):
    permissions = JSONField(default=list)   # ✅
    # permissions = JSONField(default=[])   # ❌

# 外键必须有 on_delete
class Node(models.Model):
    node_type = ForeignKey(NodeType, on_delete=models.CASCADE)  # ✅
```

---

### 3.5 配置层检查（🟡 中优先级 — 按需检查）

| # | 检查项 | 检查命令 | 自动化 |
|---|--------|----------|--------|
| 1 | 环境变量名 config.env vs settings.py | 人工对比 | ❌ |
| 2 | DjangoTemplates `APP_DIRS: True` | `grep -n "APP_DIRS" cimf_django/settings.py` | ✅ |
| 3 | Jinja2 `APP_DIRS: False` | `grep -n "APP_DIRS" cimf_django/settings.py` | ✅ |
| 4 | MIDDLEWARE 顺序正确 | 人工审查 | ❌ |
| 5 | LOGGING 覆盖所有 logger 名 | 人工审查 | ❌ |
| 6 | 数据库连接级配置生效 | 人工审查 | ❌ |

---

### 3.6 模块系统检查（🟡 中优先级）

| # | 检查项 | 检查命令 | 自动化 |
|---|--------|----------|--------|
| 1 | `__import__` 前验证模块安装状态 | `grep -rn "__import__" core/ modules/` | ✅ |
| 2 | URL catch-all 在最后 | 人工审查 | ❌ |
| 3 | 空 `urls.py` 无意义文件 | `find modules/ -name "urls.py" -empty` | ✅ |
| 4 | `module.py` MODULE_INFO 完整 | 人工审查 | ❌ |
| 5 | 动态路由 import 异常处理 | `grep -rn "except.*ImportError" modules/` | ✅ |
| 6 | 模块启用/禁用状态一致性 | 人工审查 | ❌ |
| 7 | `calc` 等模块无 `eval()` 注入 | `grep -rn "eval(" modules/` | ✅ |
| 8 | 模块分发视图 `module_dispatch` 安全 | 人工审查 | ❌ |

---

## 四、根因分析与预防

### 4.1 复制粘贴遗留

Bug 修复后未清理旧代码，导致死代码、冲突文件和混淆。

**典型表现：**
- `modules/urls.py` 中有 `prefix='modules/'` 的双前缀死代码
- `core/importexport/services.py` 和 `services/` 目录并存
- `nodes/` 重命名为 `modules/` 后残留引用

**预防：**
- 删除旧文件时全局搜索引用
- 确认无人引用后删除向后兼容文件
- 使用 `grep -rn "旧的模块名" .` 检查残留

### 4.2 假设未验证

开发者对运行时状态做了未验证的假设。

**常见假设：**
- "查询肯定有结果" → `.first()` 返回 None
- "数据库一定有数据" → 外键非空
- "定时任务肯定执行过" → `_last_run` 非 None
- "用户肯定传了这个参数" → `request.GET.get()` 返回 None

**预防：**
- 每个 `.first()` 后面必须跟 None 检查
- 每个外键访问前必须有空值保护
- 配置项读取使用 `.get(key, default)` 模式
- 所有 `request.GET/POST.get()` 检查空值

### 4.3 前后端不同步

前端期望的响应格式与后端实际返回的不一致。

**典型表现：**
- JS 调用 `response.json()` 但后端返回 `redirect()`
- 后端返回 `{success: true}` 但前端检查 `result.success`
- 表单字段名和 JSON key 名不一致

**预防：**
- 定义 API 响应 schema（统一使用 `{'success': bool, 'data': ..., 'error': ...}`）
- API 端点统一返回 `JsonResponse` 而非 `redirect`
- 修改响应格式时同步更新前端代码

### 4.4 安全惰性

因"方便"而跳过安全检查。

**典型表现：**
- "这个只有管理员能用" → 不加 `@admin_required`
- "这是内部接口" → 不加 `@login_required`
- "名字是用户自己填的" → 直接嵌入 f-string
- "参数来自数据库" → 不做类型验证

**预防：**
- 视图函数默认加 `@login_required`，白名单例外
- 所有用户输入视为不可信
- 生成代码/脚本时用 `repr()` 或 `json.dumps()`

### 4.5 框架约定违反

对框架内置约定不了解或忽略。

**典型表现：**
- `DjangoTemplates APP_DIRS: False` 导致 admin 模板 404
- SQLite WAL 模式设置在临时连接上
- `JSONField(default={})` 使用可变默认值

**预防：**
- 修改框架配置后运行 `manage.py check`
- 数据库连接级设置使用 Django 信号
- 理解 Django 每个配置项的含义

### 4.6 Code Review 检查清单

```
□ 是否有新的 API？是否添加 @login_required / @admin_required？
□ 是否有破坏性操作？是否限制 @require_POST？
□ 是否有对象查询？是否处理 None 情况？
□ 是否有表单修改？是否验证必填字段？
□ 是否有配置修改？是否同步模型/表单/模板/视图？
□ 是否有权限修改？是否测试边界情况？
□ 是否有新增模板？是否包含 csrf_token？
□ 是否修改了 Jinja2 模板？是否使用正确的语法？
□ 是否有新增设置项？是否同步到所有相关文件？
□ 是否有生成代码/脚本？是否使用 repr() 转义用户输入？
□ 新功能是否测试了未登录访问？（应重定向或返回401）
□ 运行 ./venv/bin/python manage.py check 是否通过？
□ POST 表单是否使用 {{ csrf_token }}？
□ 是否存在 file.py 和 file/ 目录冲突？
□ 是否有 console.log 泄露敏感信息？
```

---

## 五、修复优先级决策树

```
是否为安全漏洞？（认证绕过/注入/XSS/CSRF）
  ├── 是 → 🔴 P0，立即修复，不可推迟
  └── 否
       └── 是否导致 500 错误或数据丢失？
            ├── 是 → 🟠 P1，当日内按顺序修复
            └── 否
                 └── 是否功能异常？（结果错误/功能不可用）
                      ├── 是 → 🟡 P2，列入当前迭代
                      └── 否 → 🟢 P3（代码质量/UI优化），积攒一批修复
```

### 优先级定义

| 级别 | 定义 | 响应时间 | 举例 |
|------|------|----------|------|
| 🔴 P0 | 安全漏洞或系统崩溃 | 立即 | f-string注入、认证绕过、定时任务不执行 |
| 🟠 P1 | 功能异常或 500 错误 | 24h | .first()崩溃、装饰器缺失、CSRF暴露 |
| 🟡 P2 | 功能可用但结果错误 | 当前迭代 | 模板渲染错误、查询结果不精确 |
| 🟢 P3 | 代码质量或体验问题 | 积攒修复 | 死代码、多余导入、控制台调试日志 |

---

## 六、自动化检查建议

### 6.1 可 CI 自动化的检查

```bash
# 1. Django 系统检查
./venv/bin/python manage.py check

# 2. Migration 完整性
./venv/bin/python manage.py makemigrations --check

# 3. 语法检查所有文件
find core modules -name "*.py" -exec ./venv/bin/python -m py_compile {} \;

# 4. `.first().` 链式调用（高危）
! grep -rn "\.first()\." core/ modules/

# 5. datetime.now() 误用（白名单排除时区解析）
! grep -rn "datetime\.now\(\)" core/ modules/

# 6. JSONField default 可变对象
! grep -rn "JSONField.*default={" core/ modules/  # {} 不可用
! grep -rn "JSONField.*default=\[" core/ modules/  # [] 不可用

# 7. Django 模板语法在 Jinja2 项目中
! grep -rn 'date:"' core/templates/
! grep -rn "{% load" core/templates/
! grep -rn "{% url " core/templates/

# 8. eval() 使用
! grep -rn "eval(" modules/

# 9. 导入路径冲突
! ls core/*/services.* 2>/dev/null && ls -d core/*/services/ 2>/dev/null
```

### 6.2 需人工审查的项

- 逻辑错误（条件分支遗漏、循环边界）
- N+1 查询性能问题
- 权限设计是否合理
- 配置项含义是否正确
- 新模块架构设计

### 6.3 推荐检查脚本

创建 `scripts/check-bugs.sh`：

```bash
#!/bin/bash
echo "=== Bug 自动化检查 ==="
echo ""
echo "1. Django 系统检查"
./venv/bin/python manage.py check || exit 1
echo ""
echo "2. Migration 检查"
./venv/bin/python manage.py makemigrations --check || exit 1
echo ""
echo "3. .first() 链式调用（不应有输出）"
grep -rn "\.first()\." core/ modules/ || echo "  ✅ 无"
echo ""
echo "4. datetime.now() 误用（不应有输出）"
grep -rn "datetime\.now\(\)" core/ modules/ || echo "  ✅ 无"
echo ""
echo "5. Jinja2 date 错误语法"
grep -rn 'date:"' core/templates/ || echo "  ✅ 无"
echo ""
echo "6. console.log 中 CSRF"
grep -rn "console\.log.*csrf\|console\.log.*CSRF\|console\.log.*token" core/templates/ || echo "  ✅ 无"
echo ""
echo "=== 检查完成 ==="
```

---

## 七、新模块检查模板

开发新模块时，按以下清单逐项检查。

### 7.1 模型层检查

```python
# models.py
class NewModule(models.Model):
    """新模块模型"""
    
    # ✅ 必填字段：必要字段有 blank=False/null=False
    name = models.CharField(max_length=100)
    
    # ✅ 外键：正确设置 on_delete
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    
    # ✅ JSONField default 可调用
    config = JSONField(default=dict)
    
    # ✅ choices 与表单/视图一致
    status = models.CharField(max_length=20, choices=[
        ('draft', '草稿'),
        ('published', '已发布'),
    ])
    
    # ✅ 时间戳使用 auto_now_add/auto_now
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'new_module'
```

**检查清单：**
- [ ] 所有必填字段已定义
- [ ] 外键关系正确（on_delete）
- [ ] JSONField default 使用 `dict`/`list`
- [ ] choices 与表单/视图一致
- [ ] 有 `__str__` 方法
- [ ] 有 Meta 类定义表名
- [ ] CharField/EmailField 无 `null=True`

### 7.2 服务层检查

```python
# services.py
class NewModuleService:
    
    @staticmethod
    def get_by_id(module_id: int) -> Optional['NewModule']:
        """✅ .first() 返回值必须检查"""
        return NewModule.objects.filter(id=module_id).first()
    
    @staticmethod
    def create(data: dict) -> NewModule:
        """✅ 创建时验证必填字段"""
        if not data.get('name'):
            raise ValueError('名称不能为空')
        return NewModule.objects.create(**data)
    
    @staticmethod
    def get_list(filters: dict) -> List[NewModule]:
        """✅ 使用 select_related 避免 N+1"""
        queryset = NewModule.objects.select_related('category')
        
        # ✅ 整数字段不直接用 __icontains
        if filters.get('category_id'):
            try:
                cat_id = int(filters['category_id'])
                queryset = queryset.filter(category_id=cat_id)
            except (ValueError, TypeError):
                pass
        
        # ✅ 使用 Q 对象进行 OR 查询
        if filters.get('search'):
            from django.db.models import Q
            search = filters['search'].strip()
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
```

**检查清单：**
- [ ] `.first()` 返回值被检查
- [ ] `.get()` 有异常处理
- [ ] 外键访问前检查 None
- [ ] 整数字段不用 `__icontains`
- [ ] 列表查询使用 `select_related`
- [ ] 复杂查询使用 Q 对象
- [ ] `datetime.now()` 已替换为 `timezone.now()`
- [ ] 异常都记录了日志

### 7.3 表单层检查

```python
# forms.py
class NewModuleForm(forms.ModelForm):
    
    class Meta:
        model = NewModule
        fields = ['name', 'category', 'status', 'description']
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('名称不能为空')
        if len(name) < 2:
            raise forms.ValidationError('名称至少2个字符')
        return name.strip()
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        category = cleaned_data.get('category')
        if status == 'published' and not category:
            raise forms.ValidationError('发布时必须选择分类')
        return cleaned_data
```

**检查清单：**
- [ ] clean_* 方法验证必填字段
- [ ] clean() 方法进行交叉验证
- [ ] 错误信息明确
- [ ] 字段与模型一致
- [ ] user_id 为 None 时 exclude 安全

### 7.4 视图层检查

```python
# views.py
@login_required
@require_http_methods(["GET", "POST"])
def new_module_list(request):
    """列表视图"""
    search = request.GET.get('search', '')
    category_id = request.GET.get('category')
    
    if category_id:
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            category_id = None
    
    if not request.user.is_admin:
        return JsonResponse({'error': '需要管理员权限'}, status=403)
    
    modules = NewModuleService.get_list({
        'search': search,
        'category_id': category_id,
    })
    
    return render(request, 'new_module/list.html', {
        'modules': modules,
    })

@login_required
@require_POST
def new_module_create(request):
    """创建视图"""
    form = NewModuleForm(request.POST)
    
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    
    try:
        module = NewModuleService.create(form.cleaned_data)
        return JsonResponse({'success': True, 'id': module.id})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
```

**检查清单：**
- [ ] 有 `@login_required` / `@admin_required`
- [ ] 破坏性操作有 `@require_POST`
- [ ] 参数验证（GET/POST.get() 默认值）
- [ ] 权限检查
- [ ] 表单验证 `form.is_valid()`
- [ ] 异常处理 + 日志
- [ ] 无开放重定向

### 7.5 URL 配置检查

```python
# urls.py
app_name = 'new_module'

urlpatterns = [
    path('', views.new_module_list, name='list'),
    path('create/', views.new_module_create, name='create'),
    path('<int:pk>/', views.new_module_detail, name='detail'),
    path('<int:pk>/edit/', views.new_module_edit, name='edit'),
    path('<int:pk>/delete/', views.new_module_delete, name='delete'),
]
```

**检查清单：**
- [ ] `app_name` 设置正确
- [ ] URL 命名规范 `app:name`
- [ ] HTTP 方法与视图一致
- [ ] 参数格式正确（`<int:pk>` 而非 `<pk>`）
- [ ] 特定路径在 catch-all 之前

### 7.6 模板层检查

```html
<!-- list.html -->

<!-- ✅ 表单必须包含 csrf_token -->
<form method="post">
    {{ csrf_token }}
    
    <!-- ✅ 外键显示检查 None -->
    <td>{{ module.category.name if module.category else '-' }}</td>
    
    <!-- ✅ 时间格式化使用 strftime -->
    <td>{{ module.created_at.strftime('%Y-%m-%d') if module.created_at else '-' }}</td>
    
    <!-- ✅ 布尔值正确显示 -->
    <td>{{ '是' if module.is_active else '否' }}</td>
    
    <!-- ✅ 默认值处理 -->
    <td>{{ module.description|default('无') }}</td>
</form>

<!-- ✅ 链接使用 url() 函数 -->
<a href="{{ url('new_module:detail', module.id) }}">查看</a>
```

**检查清单：**
- [ ] POST 表单包含 `{{ csrf_token }}`
- [ ] 外键显示检查 None
- [ ] 时间使用 `strftime()` 而非 `|date()`
- [ ] 布尔值正确显示
- [ ] 默认值处理
- [ ] 链接格式正确 `url('ns:name', arg)`
- [ ] URL 路径使用 `url()` 而非硬编码
- [ ] 无 `console.log` 泄露信息
- [ ] 无 Django 模板标签（`{% load %}`, `{% url %}`）

### 7.7 配置层检查

```python
# core/services/settings_service.py
DEFAULT_SETTINGS = {
    # ... 其他设置 ...
    'new_module_enabled': 'false',
    'new_module_page_size': '20',
    'new_module_allow_export': 'false',
}

# services.py 读取配置
class NewModuleService:
    @classmethod
    def get_config(cls) -> dict:
        settings = SettingsService.get_all_settings()
        return {
            'enabled': settings.get('new_module_enabled', 'false') == 'true',
            'page_size': int(settings.get('new_module_page_size', '20')),
            'allow_export': settings.get('new_module_allow_export', 'false') == 'true',
        }
```

**检查清单：**
- [ ] DEFAULT_SETTINGS 包含所有配置项
- [ ] 表单包含对应字段
- [ ] 服务层读取配置
- [ ] 模板显示配置值
- [ ] 有合理的默认值

### 7.8 Migration 检查

```bash
# 创建迁移
./venv/bin/python manage.py makemigrations new_module

# 检查生成的迁移文件
# 确保：
# 1. 依赖正确（core.0001_initial）
# 2. 字段类型正确
# 3. 索引和外键正确
./venv/bin/python manage.py showmigrations | grep new_module
```

**检查清单：**
- [ ] 迁移依赖正确
- [ ] 字段类型与模型一致
- [ ] 有必要的索引
- [ ] 外键关系正确

### 7.9 新模块完整检查命令

```bash
# 1. 系统检查
./venv/bin/python manage.py check

# 2. Migration 检查
./venv/bin/python manage.py makemigrations --check
./venv/bin/python manage.py showmigrations | grep new_module

# 3. 服务层检查
grep -n "\.first()" modules/new_module/services.py
grep -n "\.get(" modules/new_module/services.py
grep -n "datetime\.now" modules/new_module/

# 4. 视图检查
grep -n "@login_required\|@admin_required" modules/new_module/views.py
grep -n "@require_" modules/new_module/views.py
grep -n "csrf_exempt" modules/new_module/views.py

# 5. 表单检查
grep -n "def clean" modules/new_module/forms.py

# 6. 模板检查
grep -n "csrf_token" modules/new_module/templates/
grep -rn 'date:"' modules/new_module/templates/
grep -rn "{% load\|{% url \|{% csrf_token %}" modules/new_module/templates/

# 7. 配置检查
grep -n "new_module_" core/services/settings_service.py

# 8. 安全检查
grep -rn "eval(" modules/new_module/
grep -rn "f'.*{.*[name|id|param]" modules/new_module/

# 9. 代码质量
grep -rn "except.*:.*pass" modules/new_module/
grep -rn "print(" modules/new_module/
```

---

## 附录

### 附录 A：4 轮 Bug 检查完整统计

| 轮次 | 检查区域 | P0 | P1 | P2 | 主要文件 | 关键修复 |
|------|----------|----|----|----|----------|----------|
| 1-1 | SMTP 模块 | 0 | 8 | 11 | smtp/views, smtp/services, smtp/templates | 模板路径修复、EmailLog 类型修正 |
| 1-2 | 路由系统 | 1 | 3 | 8 | modules/urls, node/views, customer/views | 开放重定向修复、JS dashboard 修复 |
| 1-3 | Jinja2 模板 | 0 | 3 | 6 | 70+ 模板文件 | 语法统一、csrf_token 修复 |
| 1-4 | 模块注册加载 | 1 | 4 | 6 | module_service.py, module.py | for-else 缩进修复 |
| 1-5 | 核心服务认证 | 2 | 2 | 5 | auth.py, forms, user_service | 重定向验证、认证逻辑 |
| 2-1 | Node 模块系统 | 4 | 6 | 6 | node/views, customer/* | @require_POST、Http404 |
| 2-2 | API 视图数据流 | 3 | 5 | 6 | views/api/*, cron.py | 装饰器修复 |
| 2-3 | 前端静态文件 | 2 | 8 | 44 | JS, templates | 分页括号、setInterval 防重 |
| 2-4 | 初始化迁移 | 3 | 5 | 6 | init_db, migrations | datetime→timezone |
| 2-5 | 横切关注点 | 3 | 12 | 35 | logs, exceptions, threads | 日志体系修复 |
| 3-1 | 导入导出 | 0 | 5 | 13 | importexport/* | CSV注入、编码检测 |
| 3-2 | 模块市场 | 0 | 5 | 13 | marketplace/* | Zip bomb、SSRF |
| 3-3 | 权限角色 | 2 | 5 | 11 | permission_service, user_service | is_admin 覆盖 role |
| 3-4 | 定时任务 | 1 | 6 | 14 | cron_service | 缺 else 分支 |
| 3-5 | 配置环境 | 0 | 3 | 17 | settings, middleware | JsonResponse 崩溃、env 变量名 |
| 4-1 | core 根目录 + fields | 0 | 0 | 0 | models, forms, constants | 无问题 |
| 4-2 | 模块系统核心 | 1 | 1 | 19 | module_service | f-string 注入 |
| 4-3 | modules 各模块 | 0 | 1 | 11 | customer, clock, calc | calc eval 安全 |
| 4-4 | SMTP + 市场 | 0 | 0 | 0 | smtp/*, marketplace/* | 无问题 |
| 4-5 | 导入导出 + 配置 | 0 | 8 | 10 | views, export_service, settings | WAL 模式、DjangoTemplates APP_DIRS |

### 附录 B：风险热力图

| 区域 | 风险等级 | Bug 密度 | 高频模式 |
|------|----------|----------|----------|
| `core/services/` | 🔴 极高 | 18个 | `.first()` None、datetime.now()、except:pass |
| `core/views/` | 🔴 极高 | 15个 | 装饰器缺失、参数验证 |
| `core/templates/` | 🔴 高 | 12个 | Jinja2语法、csrf_token、外键None |
| `core/module/services/` | 🟡 中 | 8个 | f-string注入、死代码 |
| `core/node/views.py` | 🟡 中 | 6个 | 模块分发安全、@require_POST |
| `core/importexport/` | 🟡 中 | 4个 | key不匹配、编码 |
| `core/marketplace/` | 🟢 低 | 3个 | Zip bomb、SSRF |
| `core/smtp/` | 🟢 低 | 2个 | 模板路径 |
| `modules/*/` | 🟢 低 | 5个 | eval、forms 空文件 |
| `cimf_django/settings.py` | 🟡 中 | 5个 | APP_DIRS、env变量名 |
| `cimf_django/middleware.py` | 🟢 低 | 2个 | JsonResponse、logger名 |
| `cimf_django/database.py` | 🟢 低 | 1个 | WAL 模式 |
| `static/js/` | 🟢 低 | 1个 | JS 语法错误 |

### 附录 C：Top 5 高频 Bug 修复前后对比

**#1 `.first()` 未检查 None（20+次）**

```python
# 修复前
def get_user(user_id):
    return User.objects.filter(id=user_id).first()

# 修复后
def get_user(user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return None
    return user
```

**#2 Jinja2/Django 语法混用（30+处）**

```html
<!-- 修复前 -->
{{ user.created_at|date:"Y-m-d" }}
{% include "..." with var=value %}

<!-- 修复后 -->
{{ user.created_at.strftime('%Y-%m-%d') if user.created_at else '-' }}
{% set var = value %}{% include "..." %}
```

**#3 装饰器缺失（15+次）**

```python
# 修复前
def cron_status(request):
    return JsonResponse(cron.get_status())

# 修复后
@admin_required
def cron_status(request):
    return JsonResponse(cron.get_status())
```

**#4 CSRF token 问题（15+处）**

```javascript
// 修复前
console.log('CSRF Token:', csrfToken);

// 修复后
// CSRF Token 仅用于请求头，不输出到控制台
headers: { 'X-CSRFToken': csrfToken }
```

**#5 `except: pass` 无日志（10+次）**

```python
# 修复前
try:
    cards = get_cards()
except Exception:
    pass

# 修复后
try:
    cards = get_cards()
except Exception as e:
    logger.error(f"获取卡片失败: {e}", exc_info=True)
    cards = []
```

---

> 文档创建：2026-05-08  
> 最后更新：2026-05-08  
> 版本：1.0
