# Bug 模式扫描与 run.sh 重构计划

> 对应 AGENTS.md 中「将潜在 Bug 通过脚本检测生成 JSON 报告，再由 AI 修复」
> 开发阶段：Stage 4 → Stage 5
> 预计工作量：~380 行 Python + ~25 行 shell 修改
> 执行时间：< 5 秒（全量扫描 120 文件）

---

## 1. 目标

1. **创建 `bugscan` 管理命令** — 将 6 类已知 Bug 模式操作化，输出 JSON 报告供 AI 直接使用
2. **合并 run.sh 维护菜单检查项** — 4 个分散检查合并为「全面检查」，新增「Bug 模式扫描」
3. **建立 `.bugscanignore` 机制** — 已知误报抑制，避免重复检出

---

## 2. 文件清单

### 2.1 新增文件

| # | 文件 | 行数 | 内容 |
|:-:|------|:----:|------|
| 1 | `.bugscanignore` | ~20 | 初始抑制规则 |
| 2 | `core/bugscan/__init__.py` | 1 | 空包 |
| 3 | `core/bugscan/ignore.py` | ~40 | `.bugscanignore` 解析器 |
| 4 | `core/bugscan/detectors.py` | ~200 | 6 个检测器 |
| 5 | `core/bugscan/reporter.py` | ~50 | JSON 报告生成 + 文件写入 + 保留策略 |
| 6 | `core/management/commands/bugscan.py` | ~70 | CLI 入口，编排检测流程 |

### 2.2 修改文件

| 文件 | 变更 |
|------|------|
| `run.sh` | 维护菜单 6-9 → 6(全面检查) 7(Bug模式扫描) |
| `.gitignore` | 添加 `storage/reports/bugscan_*.json` |

---

## 3. 检测器设计

### 3.1 L1 检测器（grep，瞬间完成）

| ID | 检测目标 | 方法 | 严重度 |
|----|---------|------|:------:|
| `datetime_now` | `datetime.now()` 无时区参数 | `grep` | high |
| `jsonfield_default` | `JSONField(default={}/[])` 可变默认值 | `grep` | critical |
| `nullbooleanfield` | `NullBooleanField()` 弃用 | `grep` | medium |

### 3.2 L2 检测器（AST，< 5 秒）

| ID | 检测目标 | 方法 | 严重度 |
|----|---------|------|:------:|
| `first_unchecked` | `.first()` 结果在同一函数内使用前未检查 None | AST 变量追踪 | high |
| `first_returned` | `.first()` 结果直接 return（调用者负责） | AST 变量追踪 | low |
| `save_no_updates` | `.save()` 无 `update_fields`（过滤非 Django save）| AST 调用分析 | medium |
| `modelchoice_static` | `ModelChoiceField(queryset=...)` 非 `.none()` 静态 | AST 类体分析 | high |

### 3.3 first_unchecked AST 变量追踪算法

```
输入: x = QuerySet.first()
输出: SameFunctionBlockScope

1. 找到包含 x 赋值的 FunctionDef / AsyncFunctionDef 或 模块级代码块
2. 在 x 赋值语句之后遍历同一块的 body
3. 对每个遇到的可能引用 x 的语句:
   a. if not x / if x is None / if x: → 终止（已检查，OK）
   b. return x → first_returned (low)
   c. x.attr / fun(x) → first_unchecked (high)
   d. 若 x 未被引用 → 到块末尾仍无引用 → 标记为 first_returned (low)
```

### 3.4 非 Django save 过滤

```
.save() 调用的对象如果是以下属性链 → 跳过:
  - wb.save(...)      (openpyxl Workbook)
  - img.save(...)     (PIL Image)
  - image.save(...)   (PIL Image)
  - result.save(...)   (PIL Image 返回结果)
```

判别方法：检查 `.save()` 的调用者（call.func.value）名称是否在排除列表中。

---

## 4. `.bugscanignore` 格式

```gitignore
# 注释（行首 #）

# 忽略整个文件所有检测
core/checks.py

# 忽略某文件:行:特定类型
core/services/sample_data_service.py:27:first_unchecked

# 忽略某文件所有特定类型的检测
core/services/base_service.py:first_returned

# 忽略某文件某行的所有检测类型
core/services/user_service.py:255

# 支持 glob 通配符
modules/*/services.py:first_returned
```

### 4.1 语法解析流程

```
行 → 去除尾部 # 注释 → 按 : 分割
  [0] file_pattern    : 必选，支持 fnmatch glob
  [1] line            : 可选，整数
  [2] pattern_id      : 可选，检测器标识
```

### 4.2 抑制匹配逻辑

```python
def is_ignored(file, line, pattern_id, rules):
    for rule in rules:
        if not fnmatch(file, rule.file_pattern):
            continue
        if rule.line is not None and rule.line != line:
            continue
        if rule.pattern_id is not None and rule.pattern_id != pattern_id:
            continue
        return True  # 匹配
    return False
```

---

## 5. JSON 报告格式

```json
{
  "version": "1.0",
  "timestamp": "2026-07-22T14:30:00+08:00",
  "ignored": {
    "count": 16,
    "rules_applied": 9
  },
  "findings": [
    {
      "file": "core/management/commands/maintenance.py",
      "line": 50,
      "column": 13,
      "severity": "high",
      "pattern_id": "datetime_now",
      "code": "        timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")",
      "message": "datetime.now() 缺少时区参数，应使用 timezone.now()",
      "fix_hint": "from django.utils import timezone → timezone.now()"
    }
  ],
  "summary": {
    "total": 1,
    "by_severity": {
      "critical": 0,
      "high": 1,
      "medium": 0,
      "low": 0
    },
    "by_pattern": {
      "datetime_now": 1,
      "jsonfield_default": 0,
      "nullbooleanfield": 0,
      "first_unchecked": 0,
      "first_returned": 0,
      "save_no_updates": 0,
      "modelchoice_static": 0
    }
  },
  "stats": {
    "files_scanned": 87,
    "execution_time_ms": 1520,
    "report_file": "storage/reports/bugscan_20260722_143000.json"
  }
}
```

---

## 6. run.sh 维护菜单变更

### 当前 (7 项)

```
  1 → 数据库备份
  2 → 清理缓存
  3 → 查看环境变量
  4 → 杀死服务器进程
  5 → 下载/更新省市区数据
  6 → Ruff 代码检查
  7 → Deploy 安全检查
  8 → 模板问题检查
  9 → 全面 Bug 预检查
  0 → 返回主菜单
```

### 变更后 (7 项)

```
  1 → 数据库备份
  2 → 清理缓存
  3 → 查看环境变量
  4 → 杀死服务器进程
  5 → 下载/更新省市区数据
  6 → 全面检查 (Ruff + Deploy + 模板 + Bug 预检查)
  7 → Bug 模式扫描 (bugscan)
  0 → 返回主菜单
```

### 6.1 `run_all_checks()` 实现

```bash
run_all_checks() {
    run_ruff_check
    run_deploy_check
    run_template_check
    run_bug_precheck
    echo -e "\n${GREEN}全部检测完成，报告已保存到 storage/reports/${NC}"
}
```

---

## 7. 初始 `.bugscanignore` 内容

```gitignore
# ============================================
# .bugscanignore — Bug 模式扫描抑制规则
# ============================================
# 语法: file_pattern[:line[:pattern_id]]
#   行首 # 为注释; 空白行被忽略
#   file_pattern 支持 fnmatch glob (*, ?, [seq])
#   line: 可选，整数
#   pattern_id: 可选，检测器标识

# --- 已知安全的 first_returned（调用者负责 None 检查）---
core/node/services/node_type_service.py:first_returned
core/node/services/node_service.py:first_returned
core/services/base_service.py:first_returned
core/services/taxonomy_service.py:first_returned
core/module/services/module_query_service.py:first_returned
core/importexport/fk_resolver.py:first_returned
core/importexport/services/export_service.py:first_returned
core/services/china_region_service.py:first_returned
core/smtp/services/template_service.py:first_returned
modules/customer/services.py:first_returned

# --- first_unchecked 但实际由周围逻辑保护 ---
core/services/sample_data_service.py:27:first_unchecked
core/services/sample_data_service.py:28:first_unchecked

# --- 无操作 save（changed 为空时的兜底 save）---
core/services/user_service.py:255:save_no_updates
```

---

## 8. 报告保留策略

- 写入 `storage/reports/bugscan_YYYYMMDD_HHMMSS.json`
- 每次写入后清理只保留最近 5 份（同名模式）
- 其他前缀（`ruff_*`, `deploy_*`, `templates_*`, `precheck_*`）不受影响

---

## 9. 验收条件

| # | 检查项 | 预期 |
|:-:|--------|------|
| 1 | `python manage.py bugscan` | 输出 JSON 到 stdout + 保存文件 |
| 2 | JSON 格式符合第 5 节 Schema | schema 验证通过 |
| 3 | `.bugscanignore` 抑制检查 | 16 条规则生效，0 条违反 |
| 4 | 维护菜单 6 → 全面检查 | 4 项顺序执行，各出独立报告 |
| 5 | 维护菜单 7 → Bug 模式扫描 | 执行 `manage.py bugscan` |
| 6 | 报告保留策略 | 最多 5 份 bugscan_*.json |
| 7 | `manage.py check --tag cimf` | 无新增警告（仍为 8 项已知） |
