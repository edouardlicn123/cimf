# LINE 模块实施计划

## 1. 概述

### 1.1 目标

新建 `modules/line/` 模块，仿照 WhatsApp 模块的架构，实现使用 CHRLINE-Patch 库的 LINE 号码检测与加好友功能。

### 1.2 确认的决策

| 问题 | 决策 |
|------|------|
| `has_line` 字段位置 | 加在 `CustomerFields` 模型（`BooleanField(null=True)`），与 `has_whatsapp` 一致 |
| CHRLINE authToken 过期 | 自动登录 + 加密保存 token 到数据库 |
| 分批查询方式 | 仿 WhatsApp：每批 10 个号码，批间间隔 3~5 秒（随机化），保留进度展示和停止能力 |
| 功能范围 | 一次性包含 **check only**（查号码是否有 LINE）+ **add friend**（加好友） |

### 1.3 不包含的功能

| 功能 | 理由 |
|------|------|
| 发送消息 | CHRLINE-Patch 支持 `sendMessage()`，但因为是逆向工程 API，批量发消息封号风险极高（error 100 = 永久封号）。作者明确说"仅供调试"。不与包含 |
| 定时任务 | 加好友是一次性操作，不需要定时调度 |
| 设置管理页面 | LINE 不需要 host/port 配置（CHRLINE 是本地模拟客户端，非外部服务） |
| 日限额 | 无发送功能，不需要限额 |

---

## 2. 文件清单

### 2.1 新建文件（12 个）

```
modules/line/
├── __init__.py                    # 空文件
├── apps.py                        # LineConfig（label='line'）
├── module.py                      # MODULE_INFO
├── models.py                      # CheckBatch, CheckLog, LineAuth, LineContact
├── services.py                    # LineService
├── views.py                       # 页面 + API 视图
├── urls.py                        # URL 路由
├── requirements.txt               # CHRLINE-Patch>=2.6.0
├── migrations/
│   ├── __init__.py                # 空文件
│   └── 0001_initial.py            # 自动生成
└── templates/
    └── line/
        ├── check.html             # 号码检测页面
        ├── check_logs.html        # 验证日志页面
        └── dashboard_card.html    # 仪表盘卡片
```

### 2.2 修改文件（5 个）

| 文件 | 操作 |
|------|------|
| `modules/customer/models.py` | CustomerFields 增加 `has_line` 字段 |
| `core/views/api/cards.py` | 在 `api_dashboard_cards` 中添加 LINE 登录状态注入（仿 WhatsApp 第 86-93 行模式） |
| `docs/现有模块.md` | 添加 line 模块条目 |
| `docs/模块快照/line.md` | 新建模块快照文档 |
| `modules/urls.py` | 不需要修改（自动动态挂载 tool 类型模块） |

### 2.3 需要安装的依赖

```
pip install "CHRLINE-Patch>=2.6.0"
```

CHRLINE-Patch 会自动安装依赖：pycryptodome, xxhash, httpx[http2], thrift 等。

---

## 3. 模型设计

基于 WhatsApp 的 `CheckBatch` / `CheckLog`，加上 LINE 特有的认证和联系人存储。

### 3.1 CheckBatch（验证批次）

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | CharField (choices: running/completed/stopped/error) | 批次状态 |
| `total_count` | IntegerField (default=0) | 总数 |
| `checked_count` | IntegerField (default=0) | 已检查数 |
| `has_line_count` | IntegerField (default=0) | 有 LINE 数 |
| `no_line_count` | IntegerField (default=0) | 没有 LINE 数 |
| `invalid_count` | IntegerField (default=0) | 无效号码数 |
| `format_issue_count` | IntegerField (default=0) | 格式异常数（与 WhatsApp 一致） |
| `error_message` | TextField (null) | 错误信息 |
| `started_at` | DateTimeField (auto_now_add) | 开始时间 |
| `completed_at` | DateTimeField (null) | 完成时间 |

Meta: `db_table='line_check_batch'`, `ordering=['-started_at']`, `__str__` = `f'验证批次 {self.id} - {self.status}'`

### 3.2 `CheckLog`（验证日志）

| 字段 | 类型 | 说明 |
|------|------|------|
| `batch` | ForeignKey → CheckBatch (CASCADE) | 关联批次 |
| `customer_id` | IntegerField | 客户 ID |
| `customer_name` | CharField(100) | 客户名称 |
| `phone` | CharField(30) | 电话号码 |
| `result` | CharField (choices: has_line/no_line/invalid/error) | 验证结果 |
| `attempts` | IntegerField (default=1) | 检查次数 |
| `attempt_details` | JSONField (default=list) | 检查详情 |
| `checked_at` | DateTimeField (auto_now_add) | 检查时间 |

Meta: `db_table = 'line_check_log'`, `ordering=['-checked_at']`, `__str__` = `f'{self.phone} - {self.result}'`

### 3.3 `LineAuth`（LINE 认证信息）

| 字段 | 类型 | 说明 |
|------|------|------|
| `email` | CharField(100) | LINE 登录邮箱（加密存储） |
| `encrypted_password` | TextField | 加密的登录密码（仅首次登录后使用，后续用 token） |
| `encrypted_token` | TextField | 加密的 authToken |
| `last_login_at` | DateTimeField (null) | 最后登录时间 |
| `updated_at` | DateTimeField (auto_now) | 更新时间 |

Meta: `db_table = 'line_auth'`, `verbose_name = 'LINE 认证信息'`

**凭证来源**：首次通过管理界面 UI 表单设置 email + password（使用 Django Admin 或自定义页面），加密存储到 LineAuth。`login()` 方法优先使用 authToken 登录，过期后自动用 email+password 重新获取 token。

### 3.4 `LineContact`（已添加的 LINE 好友）

| 字段 | 类型 | 说明 |
|------|------|------|
| `customer_id` | IntegerField (null) | 关联客户 ID（用于查回来源客户） |
| `mid` | CharField(100, unique) | LINE 用户 MID |
| `phone` | CharField(30) | 电话号码 |
| `display_name` | CharField(200) | 显示名称 |
| `status` | CharField (choices: active/blocked/deleted, default='active') | 好友状态 |
| `added_at` | DateTimeField (auto_now_add) | 添加时间 |

Meta: `db_table = 'line_contact'`, `ordering=['-added_at']`, `__str__` = `f'{self.display_name} ({self.phone})'`

### 3.5 `CustomerFields.has_line` 字段追加

```python
has_line = models.BooleanField(
    null=True, blank=True, default=None,
    verbose_name='有 LINE',
    help_text='True=有, False=没有, None=未检测'
)
```

---

## 4. 服务层设计

`LineService` 类，约 15 个静态方法，仿照 `WhatsAppService` 结构。

### 4.1 核心方法

| 方法 | 说明 |
|------|------|
| `login(email, password) → dict` | 使用邮箱+密码登录 LINE 并获取 authToken，加密保存到 LineAuth |
| `_ensure_logged_in() → bool` | 检查 authToken 有效性，无效则用保存的凭据重新登录 |
| `get_status() → dict` | 返回登录状态（connected/user/error，对应 `_cl` 对象是否存在且有效） |
| `check_health() → dict` | 健康检查：尝试调用一个最小权限 API 验证连接是否真正有效 |
| `ensure_healthy() → bool` | 发送前确保连接健康，不健康则自动重连 |
| `reconnect() → bool` | 强制重新连接 LINE（清除 `_cl` 并重新登录） |

**全局单例**：
```python
_cl: CHRLINE | None = None  # 进程级单例 CHRLINE 客户端
```

### 4.2 号码检测方法

| 方法 | 说明 |
|------|------|
| `find_contacts_by_phone(phones: list) → dict` | 调用 CHRLINE `findContactsByPhone` 批量查询号码。返回 `{found: [...], not_found: [...], error: ...}` |
| `_recheck_all_task()` | 后台线程：遍历所有客户，分批检测，记录 CheckLog，每批间隔 3-5 秒随机 |
| `start_recheck_all() → dict` | 启动后台全量验证（线程） |
| `stop_recheck() → dict` | 停止验证 |
| `get_recheck_progress() → dict` | 获取验证进度 |
| `reset_check_marks() → int` | 重置 `has_line` 标记为 None |
| `_trim_check_logs(keep=4000)` | 保留最新的 keep 条日志，删除多余的（仿 WhatsApp） |

### 4.3 加好友方法

| 方法 | 说明 |
|------|------|
| `find_and_add_contacts_by_phone(phones: list) → dict` | 调用 `findAndAddContactsByPhone` 查询并添加好友，记录到 LineContact |
| `batch_add_friends(customer_ids: list) → dict` | 批量加好友：对每个号码调用，更新 has_line 和 LineContact |

### 4.4 线程安全状态变量

```python
_recheck_state = {
    'running': False,
    'batch_id': None,
    'stop_requested': False,
    'current_phone': '',
    'current_customer_name': '',
    'current_attempts': 0,
    'paused': False,
    'pause_remaining': 0,
}
```

### 4.5 验证流程

```
1. 获取所有 CustomerFields 客户（iterator）
2. 预分类：无效号码（标记 has_line=False）vs 格式异常 vs 有效号码
3. 创建 CheckBatch（total_count = 客户总数）
4. 处理无效号码（直接标记 has_line=False，创建 CheckLog，更新 invalid_count）
5. 遍历有效号码，每批 10 个号码：
   a. 调用 findContactsByPhone(batch_phones) 批量查询
   b. CHRLINE 返回的结果包含"有 LINE"的号码，未返回的视为"没有"
   c. 对每个号码：更新 has_line，创建 CheckLog
   d. 批间暂停 random.randint(3, 5) 秒
6. 完成/停止时更新 batch.status（completed/stopped/error）
7. 所有异常捕获：设置 batch.status='error' + error_message
8. 最终清理 _recheck_state
```

**注意**：失败重试逻辑—仿 WhatsApp，每个号码尝试 3 次，3 次都失败才标记 error。但 CHRLINE 的 `findContactsByPhone` 是批量查询，所以重试粒度是「整批重试最多 3 次」，而不是逐个号码重试。

---

## 5. 视图层设计

### 5.1 页面视图（`@login_required`）

| 视图 | 路由 | 说明 |
|------|------|------|
| `check_view` | `/modules/line/check/` | 号码检测页面 |
| `check_logs_view` | `/modules/line/check-logs/` | 验证日志页面 |

所有页面视图同时加载已安装的 tool 模块列表供侧边栏使用。

### 5.2 API 视图

| API | 方法 | 装饰器 | 路由 | 说明 |
|-----|------|--------|------|------|
| `api_status` | GET | `@login_required_json` | `/modules/line/api/status/` | LINE 登录状态 |
| `api_check_line` | POST | `@login_required_json` | `/modules/line/api/check-line/` | 批量检测号码 |
| `api_recheck_all` | POST | `@login_required_json` | `/modules/line/api/recheck-all/` | 全量验证 |
| `api_recheck_progress` | GET | `@login_required_json` | `/modules/line/api/recheck-progress/` | 验证进度 |
| `api_recheck_stop` | POST | `@login_required_json` | `/modules/line/api/recheck-stop/` | 停止验证 |
| `api_check_logs` | GET | `@login_required_json` | `/modules/line/api/check-logs/` | 验证日志列表（分页+筛选） |
| `api_reset_check` | POST | `@login_required_json` | `/modules/line/api/reset-check/` | 重置 `has_line` 标记 |
| `api_customers` | GET | `@login_required_json` | `/modules/line/api/customers/` | 客户列表（带 has_line 筛选） |

### 5.3 `api_customers` JSON 返回格式

与 WhatsApp 的 `api_customers` 一致，仅将 `has_whatsapp` 替换为 `has_line`：

```json
{
  "data": [{
    "id": 1,
    "customer_name": "...",
    "customer_code": "...",
    "phone": "...",
    "has_line": true/false/null
  }],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

### 5.4 URL 路由（`urls.py`）

```python
app_name = 'line'
urlpatterns = [
    path('check/', views.check_view, name='check'),
    path('check-logs/', views.check_logs_view, name='check_logs'),
    path('api/status/', views.api_status, name='api_status'),
    path('api/check-line/', views.api_check_line, name='api_check_line'),
    path('api/recheck-all/', views.api_recheck_all, name='api_recheck_all'),
    path('api/recheck-progress/', views.api_recheck_progress, name='api_recheck_progress'),
    path('api/recheck-stop/', views.api_recheck_stop, name='api_recheck_stop'),
    path('api/check-logs/', views.api_check_logs, name='api_check_logs'),
    path('api/reset-check/', views.api_reset_check, name='api_reset_check'),
    path('api/customers/', views.api_customers, name='api_customers'),
]
```

---

## 6. 模板设计

完全仿照 WhatsApp 模板，继承 `frames/frame_tools.html`，修改：

### 6.1 `check.html`

| 修改点 | WhatsApp 值 | LINE 值 |
|--------|-------------|---------|
| `active_section` | `whatsapp` | `line` |
| 图标前缀 | `bi-whatsapp` | `bi-line` |
| 品牌色 | Bootstrap `btn-success` (#198754) | LINE 绿 `#06C755` |
| 导航按钮 | 发送/记录/验证日志/设置 | 验证日志（仅 1 个导航按钮） |
| API 前缀 | `/modules/whatsapp/` | `/modules/line/` |
| 进度统计变量 | `hasWaCount` / `noWaCount` | `hasLineCount` / `noLineCount` |
| 服务状态 | WABridge 连接状态 | CHRLINE 登录状态 |

### 6.2 `check_logs.html`

| 修改点 | WhatsApp 值 | LINE 值 |
|--------|-------------|---------|
| 结果标签值 | `has_wa` / `no_wa` / `invalid` / `format_issue` | `has_line` / `no_line` / `invalid` |
| 筛选选项 | 全部/有WhatsApp/没有/无效/格式异常 | 全部/有LINE/没有/无效 |
| 导航按钮 | 发送/号码检测/发送记录/设置 | 号码检测（仅 1 个导航按钮） |
| API 端点 | `/modules/whatsapp/` | `/modules/line/` |

### 6.3 `dashboard_card.html`

LINE 绿 `#06C755` 渐变色，显示 LINE 连接状态（`line_connected` 变量，由 `core/views/api/cards.py` 注入）。

---

## 7. 模块注册信息

### 7.1 `module.py`

```python
MODULE_INFO = {
    'id': 'line',
    'name': 'LINE',
    'type': 'tool',
    'version': '1.0.0',
    'author': 'edouardlicn',
    'description': 'LINE 号码检测与好友添加模块',
    'require': ['customer'],
    'icon': 'bi-line',
    'frontpage_card': True,
    'install_on_init': False,
    'frontpage_card_clickable': True,
    'permissions': [
        {'key': 'check', 'name': '查看号码检测'},
        {'key': 'manage', 'name': '管理'},
    ],
    'dashboard_cards': [
        {
            'id': 'line_card',
            'name': 'LINE 检测卡片',
            'template': 'line/dashboard_card.html',
            'color_start': '#06C755',
            'color_end': '#06C755',
        }
    ],
}
```

---

## 8. 实现步骤（按顺序执行）

| # | 步骤 | 操作 | 验证方式 |
|---|------|------|----------|
| 1 | **安装依赖** | `pip install "CHRLINE-Patch>=2.6.0"` | `python -c "from CHRLINE import CHRLINE; print('ok')"` |
| 2 | **CustomerFields 加 `has_line` 字段** | 修改 `modules/customer/models.py`，执行 `makemigrations customer && migrate` | `manage.py showmigrations` |
| 3 | **创建模块骨架** | `modules/line/` 目录 + `__init__.py` + `apps.py` | 自动发现到 INSTALLED_APPS |
| 4 | **models.py** | CheckBatch + CheckLog + LineAuth + LineContact，含 Meta/db_table/`__str__` | `makemigrations line && migrate` |
| 5 | **services.py** | LineService 全部 15 个方法 + 重试机制 + 日志裁剪 | Python import 测试 |
| 6 | **views.py** | 2 个页面视图 + 8 个 API 视图 | 无 |
| 7 | **urls.py** | 路由注册 | 无 |
| 8 | **模板** | check.html、check_logs.html、dashboard_card.html | 视觉验证 |
| 9 | **module.py** | MODULE_INFO（含 author/description） | 无 |
| 10 | **requirements.txt** | `CHRLINE-Patch>=2.6.0` | 无 |
| 11 | **cards.py** | 在 `api_dashboard_cards` 中添加 LINE 状态注入（第 86-93 行后追加） | 首页卡片正确显示 LINE 连接状态 |
| 12 | **docs/现有模块.md** | 添加 line 模块条目 | 无 |
| 13 | **docs/模块快照/line.md** | 新建模块快照 | 无 |
| 14 | **安装模块** | 通过管理界面安装 line 模块 | 侧边栏出现 LINE |
| 15 | **配置 LINE 账号** | 通过管理界面 UI 表单设置 LINE email + password（加密存储） | 无 |
| 16 | **登录测试** | API `GET /modules/line/api/status/` | 返回 connected=True |
| 17 | **号码检测测试** | 用测试号码调用检测 API | 能正确判断是否有 LINE |
| 18 | **全量验证测试** | 启动全量验证，验证进度/停止/日志/日志裁剪功能 | 完成验证批次 |

---

## 9. 安全注意事项

1. **authToken 加密存储** — 使用 Django `FERNET_KEYS` 配置加密 token 和 password，不在日志中输出
2. **LINE 账号凭据** — 存储在数据库 `LineAuth` 表中（加密字段），首次通过管理界面 UI 表单设置，**不在 `.env` 中保存**
3. **CHRLINE 登录** — 使用生产专用账号（非个人号）
4. **分批间隔** — CHRLINE 是逆向工程 API，每批间隔 3-5 秒（随机化，避免固定模式触发风控）
5. **异常处理** — 所有 CHRLINE 调用必须 try/except，捕获网络/协议/认证异常转为友好的错误消息
6. **`api_customers` JSON key** — 使用 `has_line`，与 WhatsApp 的 `has_whatsapp` 保持一致命名风格

---

## 10. 关键代码参考

### 10.1 `apps.py`

```python
from django.apps import AppConfig

class LineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.line'
    label = 'line'
    verbose_name = 'LINE 模块'
```

### 10.2 CHRLINE 登录流程

```python
from CHRLINE import CHRLINE

cl = CHRLINE(
    email, password,
    appType=CHRLINE.LINE_CHROMEOS,
    useThrift=True,
    autoE2EE=True,
)
cl.login()
token = cl.authToken
```

### 10.3 CHRLINE 查询号码

```python
# findContactsByPhone 返回有 LINE 的号码列表
# 返回值: list of dict with keys like {'mid': '...', 'displayName': '...', 'phone': '...'}
result = cl.findContactsByPhone(phone_numbers)
# result 只包含找到的号码，未找到的不在列表中

# findAndAddContactsByPhone 查询并自动发送好友申请
result = cl.findAndAddContactsByPhone(phone_numbers)
```

### 10.4 `cards.py` 需添加的代码（仿 WhatsApp 第 86-93 行模式）

在 `api_dashboard_cards` 函数中，`if module_path == "whatsapp":` 块之后（约第 93 行），追加 LINE 的状态注入：

```python
if module_path == "line":
    try:
        line_mod = import_module(f"modules.{module_path}.services")
        if hasattr(line_mod, "LineService"):
            line_status = line_mod.LineService.get_status()
            render_context["line_connected"] = line_status.get("connected", False)
    except Exception:
        logger.warning("LINE 状态加载失败", exc_info=True)
```

---

## 11. 风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| LINE 账号被封 | 中 | 高（无法继续使用该账号） | 使用生产专用号，不做批量发送消息 |
| CHRLINE 协议兼容性 | 低 | 中（检测功能不可用） | 关注 WEDeach/CHRLINE-Patch 更新 |
| 检测速度限制 | 中 | 低（检测变慢） | 控制批大小(10)和间隔(3-5s)，整批重试最多 3 次 |
| Python 版本兼容 | 低 | 高（无法运行） | 当前 Python 3.12.3 满足要求（CHRLINE 要求 3.8+） |
| 加密密钥丢失 | 低 | 中（无法自动登录） | LineAuth 中的加密凭证依赖 Django FERNET_KEYS 配置，需在 `.env` 中设置并妥善保管 |
| 凭证存储自相矛盾 | 已修复 | — | 第 9.2 条明确凭据通过管理界面 UI 设置（非 `.env`） |