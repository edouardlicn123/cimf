# Bug 排查技术规范

> Quick reference — daily bug checking  
> 详细材料见 `docs/技术规范/A08_补充材料.md`

---

## 一、总则

### 1.1 目的与范围

本规范旨在为项目 Bug 排查提供系统化、可重复的检查流程和判断标准。适用于：日常 Code Review、上线前回归检查、专项 Bug 排查、新模块自检。

### 1.2 Bug 统计总览

| 严重程度 | 数量 | 占比 | 典型问题 |
|----------|------|------|----------|
| 🔴 P0（安全/崩溃） | 7 | 12% | f-string注入、开放重定向、定时任务仅执行一次、for-else缩进、JS语法错误 |
| 🟠 P1（功能异常） | 38 | 63% | 装饰器缺失、.first()未检查、模板语法错误、CSRF暴露 |
| 🟡 P2（代码质量） | 15 | 25% | 死代码、多余导入、logger使用不当 |

| 层级 | Bug数 | 主要问题 |
|------|-------|----------|
| 服务层 | 18 | `.first()` None检查、`datetime.now()`、`except:pass` |
| 视图层 | 15 | 装饰器缺失、CSRF处理、参数验证 |
| 模板层 | 12 | Jinja2语法混用、csrf_token语法、外键None |
| 模块系统 | 8 | 动态加载安全、f-string注入、死代码 |
| 配置层 | 5 | 环境变量不匹配、APP_DIRS、WAL |
| 导入导出 | 4 | CSV注入、编码崩溃、key不匹配 |

### 1.3 核心原则

1. **防御性编程**：结果非 None、非空、有效后再操作
2. **信任但验证**：前端验证≠后端安全，表单验证≠视图安全，已认证≠权限足够
3. **分层检查**：服务层 → 模型层 → 视图层 → 模板层 → 配置层（高→低优先级）

---

## 二、高频 Bug 模式目录

| ID | 问题 | 层级 | 快速修复 | 严重度 |
|----|------|------|----------|--------|
| BP01 | `.first()` 未检查 None | service | `.first()` 后立即 `if not result: return` | ★★★★★ |
| BP02 | Jinja2/Django 模板语法混用 | template | `\|date:`→`strftime()`, `{% csrf_token %}`→`{{ csrf_token }}`, 用 `url('ns:name', arg)` | ★★★★☆ |
| BP03 | `@login_required`/`@admin_required` 缺失 | view | 非登录页加 `@login_required`，管理操作加 `@admin_required` | ★★★★☆ |
| BP04 | `@require_POST` 缺失 | view | 所有 DELETE/CREATE/TOGGLE 操作加 `@require_POST` | ★★★★☆ |
| BP05 | CSRF Token 错误使用 | template/view | `{{ csrf_token }}` 变量，不从 console 输出，视图传 `csrf_token_value` | ★★★★☆ |
| BP06 | `except: pass` 静默吞噬异常 | service | 每个 `except` 块至少记录 `logger.warning()`/`error()` | ★★★☆☆ |
| BP07 | 外键访问前未检查 None | service/template | `obj.fk.name if obj.fk else '-'` | ★★★☆☆ |
| BP08 | `datetime.now()` 应使用 `timezone.now()` | service | 替换为 `from django.utils.timezone import now` | ★★★☆☆ |
| BP09 | JSONField default 使用可变对象 | model | `default=dict`/`list` 而非 `default={}`/`[]` | ★★☆☆☆ |
| BP10 | f-string 用户输入注入 | service | 嵌入代码用 `repr()` 或 `json.dumps()` | ★★☆☆☆ |
| BP11 | 整数类型字段使用 `__icontains` | service | 先 `int()` 转换后 `filter(id=val)` | ★★☆☆☆ |
| BP12 | 键名不匹配（生产者 vs 消费者） | all | 明确 schema，重构时同步更新所有读写方 | ★★☆☆☆ |
| BP13 | 环境变量名不匹配 | config | `config.env` 与 `settings.py` 变量名严格一致 | ★★☆☆☆ |
| BP14 | 配置与代码不一致 | config | `DjangoTemplates APP_DIRS: True`，`Jinja2 APP_DIRS: False` | ★★☆☆☆ |
| BP15 | `{% block %}` 名称不匹配 | template | 子模板 block 名与父模板严格一致 | ★★☆☆☆ |
| BP16 | 导入路径冲突（文件 vs 目录） | all | 不存在 `file.py` 和 `file/` 目录并存 | ★☆☆☆☆ |
| BP17 | `is_admin` 覆盖 `role` 逻辑 | service | `role` 分支不修改 `is_admin` | ★☆☆☆☆ |
| BP18 | 定时任务缺 else 分支 | service | 检查所有 `if/elif/else` 是否遗漏分支 | ★☆☆☆☆ |

---

## 三、按层级的防御性检查清单

> 🔴 高优先级（服务层+视图层）默认必查；🟡 中优先级（模板/模型/配置）按需检查。

### 3.1 服务层检查（🔴 必查）

| # | 检查项 | 检查命令 |
|---|--------|----------|
| 1 | `.first()` 返回值检查 None | `grep -rn "\.first()" core/ modules/` |
| 2 | `.first().property` 链式调用 | `grep -rn "\.first()\." core/ modules/` |
| 3 | `datetime.now()` 误用 | `grep -rn "datetime\.now\|from datetime import" core/ modules/` |
| 4 | `except: pass` 无日志 | `grep -rn "except.*:\s*pass" core/ modules/` |
| 5 | JSONField default 为 `{}`/`[]` | `grep -rn "JSONField.*default={" core/ modules/` |
| 6 | 整数字段 `__icontains` | `grep -rn "__icontains=" core/ modules/` |
| 7 | 链式 filter 应为 Q 对象 | 人工审查 |
| 8 | f-string 嵌入用户输入 | 人工审查生成代码/脚本 |
| 9 | N+1 查询 | 人工审查循环内查询 |
| 10 | 导入路径冲突 | `ls -d core/*/services.* core/*/services/ 2>/dev/null` |

### 3.2 视图层检查（🔴 必查）

| # | 检查项 | 检查命令 |
|---|--------|----------|
| 1 | `@login_required` 装饰器 | `grep -rn "@login_required\|@admin_required" core/ modules/` |
| 2 | `@require_POST` 对破坏性操作 | `grep -rn "@require_" core/ modules/` |
| 3 | 重复装饰器 | `grep -rn "@login_required.*@login_required" core/ modules/` |
| 4 | CSRF 处理正确 | `grep -rn "csrf_exempt\|csrf_token" core/views/` |
| 5 | `json.loads(request.body)` 有 try/except | `grep -rn "json.loads.*body" core/ modules/` |
| 6 | 参数类型验证（int 转换） | 人工审查 |
| 7 | 开放重定向（next 参数） | `grep -rn "next\|redirect.*request" core/views/` |
| 8 | 权限检查充分 | 人工审查 |

### 3.3 模板层检查（🟡 按需）

| # | 检查项 | 检查命令 |
|---|--------|----------|
| 1 | POST 表单含 csrf_token | `grep -rn "csrf_token\|csrfmiddlewaretoken" core/templates/` |
| 2 | Jinja2 date 语法正确 | `grep -rn 'date:"' core/templates/` |
| 3 | 外键显示检查 None | `grep -rn "\.country\|\.region\|\.type\|\.level" core/templates/` |
| 4 | extends 路径不含 core/ | `grep -rn "extends.*core/" core/templates/` |
| 5 | 无 Django 模板标签 | `grep -rn "{% load\|{% blocktrans\|{% url " core/templates/` |
| 6 | URL 使用 `url()` 函数 | `grep -rn "{{\s*url(" core/templates/` |
| 7 | block 名称与父模板一致 | 人工审查 |
| 8 | 无 console.log 暴露敏感信息 | `grep -rn "console\.log" core/templates/` |
| 9 | `{% include %}` 片段中无 `{% block %}` | 人工审查 |
| 10 | `{{ super() }}` 在重写的 block 中 | `grep -rn "block scripts\|block head" core/templates/` |

### 3.4 模型层检查（🟡 按需）

| # | 检查项 | 检查命令 |
|---|--------|----------|
| 1 | JSONField default 可调用 | `grep -rn "JSONField" core/ modules/` |
| 2 | ForeignKey on_delete 正确 | `grep -rn "ForeignKey" core/ modules/` |
| 3 | `__str__` 返回非空 | `grep -rn "def __str__" core/ modules/` |
| 4 | CharField/EmailField 无 `null=True` | `grep -rn "CharField.*null=T\|EmailField.*null=T" core/ modules/` |
| 5 | Meta 类完整 | 人工审查 |
| 6 | 表名唯一 | 人工审查 |

### 3.5 配置层检查（🟡 按需）

| # | 检查项 | 检查命令 |
|---|--------|----------|
| 1 | 环境变量名一致 | 人工对比 |
| 2 | DjangoTemplates `APP_DIRS: True` | `grep -n "APP_DIRS" cimf_django/settings.py` |
| 3 | Jinja2 `APP_DIRS: False` | `grep -n "APP_DIRS" cimf_django/settings.py` |
| 4 | MIDDLEWARE 顺序正确 | 人工审查 |
| 5 | LOGGING 覆盖所有 logger 名 | 人工审查 |
| 6 | 数据库连接级配置生效 | 人工审查 |

### 3.6 模块系统检查（🟡 按需）

| # | 检查项 | 检查命令 |
|---|--------|----------|
| 1 | `__import__` 前验证模块安装状态 | `grep -rn "__import__" core/ modules/` |
| 2 | URL catch-all 在最后 | 人工审查 |
| 3 | 空 `urls.py` 无意义文件 | `find modules/ -name "urls.py" -empty` |
| 4 | `module.py` MODULE_INFO 完整 | 人工审查 |
| 5 | 动态路由 import 异常处理 | `grep -rn "except.*ImportError" modules/` |
| 6 | 模块启用/禁用状态一致性 | 人工审查 |
| 7 | `eval()` 注入 | `grep -rn "eval(" modules/` |
| 8 | 模块分发视图安全 | 人工审查 |

---

## 四、根因分析与预防

| 根因 | 典型表现 | 预防措施 |
|------|----------|----------|
| 复制粘贴遗留 | 死代码、冲突文件（file.py + file/）、旧模块引用 | 删除前全局搜索引用；确认无人引用后删除 |
| 假设未验证 | `.first()`→None、外键为空、配置缺省、参数缺省 | 每个 `.first()` 后检查 None；外键访问前空值保护 |
| 前后端不同步 | 响应格式不匹配、字段名不一致 | 统一 API schema（`{success, data, error}`）；同步更新 |
| 安全惰性 | 不加装饰器、不转义输入、不做类型验证 | 默认加 `@login_required`；所有输入不可信；代码生成用 `repr()` |
| 框架约定违反 | `APP_DIRS: False`、WAL 在临时连接、`JSONField(default={})` | 修改框架配置后运行 `manage.py check`；用 Django 信号 |

### Code Review 检查清单

```
□ 新 API 有 @login_required / @admin_required？
□ 破坏性操作限制 @require_POST？
□ 对象查询处理 None？
□ 表单修改验证必填字段？
□ 配置修改同步模型/表单/模板/视图？
□ 权限修改测试边界情况？
□ 新模板包含 csrf_token？
□ Jinja2 模板使用正确语法？
□ 新增设置项同步到所有相关文件？
□ 生成代码/脚本使用 repr() 转义？
□ 未登录访问重定向或返回 401？
□ POST 表单使用 {{ csrf_token }}？
□ 无 file.py 和 file/ 目录冲突？
□ 无 console.log 泄露敏感信息？
```

---

## 五、修复优先级决策树

```
是否为安全漏洞？（认证绕过/注入/XSS/CSRF）
  ├── 是 → 🔴 P0，立即修复
  └── 否
       └── 是否导致 500 错误或数据丢失？
            ├── 是 → 🟠 P1，当日内修复
            └── 否
                 └── 是否功能异常？
                      ├── 是 → 🟡 P2，当前迭代
                      └── 否 → 🟢 P3（代码质量），积攒修复
```

| 级别 | 定义 | 响应时间 | 举例 |
|------|------|----------|------|
| 🔴 P0 | 安全漏洞/系统崩溃 | 立即 | f-string注入、认证绕过、定时任务不执行 |
| 🟠 P1 | 功能异常/500 错误 | 24h | .first()崩溃、装饰器缺失、CSRF暴露 |
| 🟡 P2 | 结果错误 | 当前迭代 | 模板渲染错误、查询不精确 |
| 🟢 P3 | 代码质量 | 积攒 | 死代码、多余导入、调试日志 |

---

## 六、自动化检查建议

```bash
# 1. Django 系统检查
./venv/bin/python manage.py check
# 2. Migration 检查
./venv/bin/python manage.py makemigrations --check
# 3. .first() 链式调用
grep -rn "\.first()\." core/ modules/ || echo "✅ 无"
# 4. datetime.now() 误用
grep -rn "datetime\.now\(\)" core/ modules/ || echo "✅ 无"
# 5. JSONField default 可变对象
grep -rn "JSONField.*default={" core/ modules/ || echo "✅ 无"
grep -rn "JSONField.*default=\[" core/ modules/ || echo "✅ 无"
# 6. Jinja2 date 错误语法
grep -rn 'date:"' core/templates/ || echo "✅ 无"
# 7. eval() 使用
grep -rn "eval(" modules/ || echo "✅ 无"
# 8. 导入路径冲突
ls core/*/services.* 2>/dev/null && ls -d core/*/services/ 2>/dev/null || echo "✅ 无"
```

**需人工审查：** 逻辑错误（条件分支遗漏）、N+1 查询、权限设计、配置含义、新模块架构。

---

> 详细 Bug 模式（症状/根因/样例代码）和新模块模板见 `docs/技术规范/A08_补充材料.md`
