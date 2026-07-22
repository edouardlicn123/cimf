# Python 代码开发规范

> 文档版本：1.1 | 最后更新：2026-05-06 — 修正测试文件位置（tests.py→tests/目录拆分）

## 一、概述

### 1.1 目的与范围
本规范旨在确保项目代码的一致性、可读性和可维护性。适用于：Django Model、Service 层、View 层、Form 层、测试代码、定时任务。

### 1.2 项目架构
项目采用「主应用（`core/`）+ 子应用（`modules/`）」模式。详见 `A01_项目概述与技术架构.md`。

### 1.3 与现有文档关系
- **A02_模块技术规范.md** — 节点业务模块实现指引
- **A04_模板开发规范.md** — Jinja2 模板语法
- **A03_省市县联动字段技术规范.md** — 省市区字段 Model 定义

### 1.4 代码风格概述
| 特性 | 说明 |
|------|------|
| 注释风格 | 中文文档字符串，标准文件头模板 |
| 方法类型 | Service 层以静态方法为主 |
| 类型注解 | 参数和返回值必须使用 |
| 空值处理 | `.first()` 必须做 null 检查 |
| 权限控制 | `PermissionService` + 专用检查函数 |
| 模板引擎 | Jinja2 |

## 二、文件头部注释规范

### 2.1 编码声明
所有 Python 文件以 `# -*- coding: utf-8 -*-` 开头。

### 2.2 文档字符串模板
包含五部分：文件信息、路径、功能说明、版本、依赖。格式见补充材料。

### 2.3 版本与依赖说明
版本号后必须有说明（`- 1.0: 初始版本`），禁止只写版本号。依赖注明模块名和用途。

## 三、导入规范

### 3.1 import 分组顺序
1. Python 标准库 | 2. 第三方库 | 3. Django 核心模块 | 4. 项目内部模块 - core | 5. 项目内部模块 - modules | 6. 相对导入（当前应用内）
组间用空行分隔。

### 3.2 项目内部导入示例
使用绝对路径：`from core.models import User`。详见补充材料。

### 3.3 别名使用规范
仅在避免循环导入时使用 `User = get_user_model()`。避免不必要的别名。

### 3.4 避免循环导入
使用字符串引用：`user = models.ForeignKey('core.User', on_delete=models.CASCADE)`。

## 四、命名规范

### 4.1 模块命名
| 类型 | 规则 | 示例 |
|------|------|------|
| Python 文件 | 小写 + 下划线 | `customer_service.py` |
| Django 应用 | 小写 | `core/` |
| 业务模块目录 | 小写 + 下划线 | `modules/customer/` |
| 包目录 | 小写 + 下划线 | `services/` |

### 4.2 类命名
| 类型 | 规则 | 示例 |
|------|------|------|
| Django Model | 大驼峰 | `class User` |
| Service | 大驼峰 + Service | `class CustomerService` |
| Form | 大驼峰 + Form | `class LoginForm` |
| View 函数 | 小写 + 下划线 | `def node_list(request)` |
| Test Case | 大驼峰 + TestCase | `class UserServiceTestCase` |

### 4.3 函数命名
小写 + 下划线，动词开头：`get_customer_list()`。

### 4.4 变量与常量
变量：小写 + 下划线。常量：全大写 + 下划线。私有：`_` 前缀。

### 4.5 Django 特定命名
- `related_name`：小写复数 + 描述性后缀
- `verbose_name`：中文
- `db_table`：小写 + 下划线

## 五、类定义规范

### 5.1 Django Model 规范
Meta 顺序：字段定义 → Meta 类 → property → `__str__`。使用 TextChoices 定义枚举。`__str__` 返回有意义的字符串。

### 5.2 Service 类规范
以 `@staticmethod` 为主，方法返回 `Optional` 时做 null 检查。

### 5.3 Form 类规范
继承 `forms.Form`，字段定义合适 widget，`clean_` 方法做格式验证。

### 5.4 方法顺序规范
字段定义 → Meta 类 → property → 私有方法 → 公开方法 → 类方法 → 静态方法 → `__str__`。

## 六、函数规范

### 6.1 参数设计
使用可选参数和默认值，必须有类型注解。参数过多（>5）考虑用 Dict。

### 6.2 返回值类型注解
所有函数必须有返回值类型注解。可能为 None 用 `Optional[...]`。

### 6.3 文档字符串规范
中文文档字符串。复杂函数：功能说明、参数、返回、异常、示例。

### 6.4 lambda 与匿名函数
仅用于简单表达式。复杂逻辑使用命名函数。

## 七、Django 特定规范

### 7.1 查询规范（.first() 空值检查）
**重要：** `.first()` 返回值必须做 null 检查（`if customer is None: return None`）。

### 7.2 外键安全访问
使用 `hasattr` 或 `if obj and obj.fk` 链式检查。推荐 Model `@property` 封装。

### 7.3 权限检查模式
视图层定义 `check_*_permission()` 返回 `(bool, str)`。使用 `@login_required` + 权限函数。

### 7.4 表单验证分层
Service 层：业务验证（唯一性等）。Form 层：格式验证。视图层分层调用。

### 7.5 消息与重定向
操作后必须 `messages.success/error` + `redirect`。

## 八、API 设计规范

### 8.1 RESTful URL 设计
API 挂载于 `/api/v1/`，使用复数名词。

### 8.2 JSON 响应格式
视图层使用 `json_success(data=None, message=None, status=200, extra=None)` 和 `json_error(message, status=400, data=None)`（位于 `core/utils/response.py`，返回 `JsonResponse`）；服务层使用 `success_response(**kwargs)` 和 `error_response(message, **kwargs)`（位于 `core/services/mixins.py`，返回 `dict`）。

### 8.3 错误响应格式
视图层 `json_error` 返回 `{'success': False, 'error': message}`（键名为 `error`，无 `code` 键）；服务层 `error_response` 返回 `{'success': False, 'error': message, **kwargs}`。

### 8.4 认证与授权
`@login_required` + `PermissionService.has_permission()`。

## 九、测试规范

### 9.1 测试文件位置
```
tests/
├── test_models.py
├── test_views.py
├── test_services.py
├── test_forms.py
├── test_api.py
└── modules/ (clock/, customer/)
```

### 9.2 测试类命名
`TestCase` 后缀：`UserServiceTestCase`。

### 9.3 setUp 方法规范
在 `setUp` 中创建测试用户和数据，供全类共享。

### 9.4 断言方法选择
使用 `assertIsNone`, `assertIn`, `assertEqual`, `assertTrue` 等。

### 9.5 - 9.6 测试示例
详见补充材料。

### 9.7 测试覆盖率要求
Service 层 ≥80% | View 层 ≥60% | Model 层 ≥50%
运行：`./venv/bin/python manage.py test`

## 十、数据库迁移规范

### 10.1 makemigrations 注意事项
使用 `--name` 参数指定有意义名称。

### 10.2 字段命名规范
小写 + 下划线。外键不加 `_id` 后缀（Django 自动）。时间字段用 `created_at`, `updated_at`。

### 10.3 外键与索引
常用查询字段加索引。唯一约束用 `unique=True`。

### 10.4 数据迁移脚本
使用 `migrations.RunPython`，提供 `reverse_code`。

### 10.5 迁移后验证
`migrate` → `showmigrations` → `check`。

### 10.6 字段空值处理规范
| 字段类型 | 规则 |
|----------|------|
| CharField/TextField/EmailField/URLField | `blank=True`（不加 `null=True`），空值用 `''` |
| ForeignKey/OneToOneField | `null=True, blank=True`，空值用 `None` |
| DateField/DateTimeField/IntegerField/JSONField | `null=True, blank=True`，空值用 `None` |
推荐使用 Django Form 处理表单数据，自动处理空值。

## 十一、定时任务规范

### 11.1 任务基类使用
继承 `CronTask`，实现 `name`, `is_enabled`, `get_interval`, `execute`。

### 11.2 任务注册与配置
在 `cron_service.py` 中：`cron.register(MyTask())`。

### 11.3 - 11.4 任务实现
详见补充材料。所有任务必须线程安全。

### 11.5 任务监控与日志
使用 `logging.getLogger(__name__)` 记录。

## 附录B 反模式速查

### B.1 查询相关
- 禁止：未检查 `.first()` 返回值
- 禁止：N+1 查询（用 `select_related` / `prefetch_related`）
- 禁止：循环中查询（用 `annotate` 聚合）

### B.2 安全相关
- 禁止：SQL 注入（用 ORM 参数化）
- 禁止：权限检查遗漏（`@login_required` + `PermissionService`）

### B.3 性能相关
- 禁止：大文本 like 查询不加限制
- 禁止：频繁无缓存调用 `SettingsService.get_setting`
- 禁止：模板中进行复杂计算

### B.4 代码风格相关
- 禁止：过长函数（拆分）
- 禁止：魔法数字（用常量/枚举）
- 禁止：空文件头注释
- 禁止：混合引号风格

## 附录C 与模板规范关联

详见 `A04_模板开发规范.md`。关键区别：
- Jinja2 过滤器用括号：`{{ value|default("x") }}`
- Jinja2 中 `{{ csrf_token }}` 不是模板标签
- Jinja2 默认自动转义

## 附录D 检查清单

### D.1 代码提交前检查
- [ ] 文件头部注释完整
- [ ] import 分组正确
- [ ] 命名符合规范
- [ ] `.first()` 有 null 检查
- [ ] 外键访问有安全保护
- [ ] 权限检查到位
- [ ] `@staticmethod` 装饰器
- [ ] 类型注解和文档字符串
- [ ] 无魔法数字/字符串
- [ ] 异常处理适当

### D.2 Django 系统检查
`./venv/bin/python manage.py check` | `./venv/bin/python manage.py showmigrations`

### D.3 测试运行检查
`./venv/bin/python manage.py test` | `./venv/bin/python manage.py test core`

## 附录E 相关文档

| 文档 | 说明 |
|------|------|
| A02_模块技术规范.md | Node 节点类型系统实现指南 |
| A04_模板开发规范.md | Jinja2 模板语法规范 |
| A03_省市县联动字段技术规范.md | 省市县三级联动字段设计 |
| docs/开发规范.md | 项目开发通用规范 |


