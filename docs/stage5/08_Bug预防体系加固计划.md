# Bug 预防体系加固计划

> 阶段 5 — 2026-07-20
> 基于 8 轮 Bug 扫描（93 项发现 + 69 项已修复）的根因分析，追加自动化检查与规范规则

---

## 背景

经过 8 轮 Bug 扫描与修复，已修复 69 项问题（P0 2/2、P1 9/9、P2 6/17、P3 5/19）。为阻止同类问题再次产生，计划加固自动化预防体系：

- **CIMF_W006**：`save()` 无 `update_fields` 检测
- **CIMF_W007**：静默 `except Exception` 检测
- 误报位置补齐意图注释
- `AGENTS.md` 追加并发安全自查项
- `run.sh` 新增选项 9 一键预检查

---

## 第一阶段：自动化检查（`core/checks.py`）

### 1. CIMF_W006 — `save()` 缺 `update_fields`

| 项目 | 说明 |
|------|------|
| 检测目标 | `core/`、`modules/` 下所有 `.py` 文件 |
| 匹配模式 | `.save()` 调用，无 `update_fields=...` 关键字参数 |
| 分析方式 | AST 扫描（同 CIMF_W003/004），定位 `ast.Call` 节点 |
| 豁免规则 | ① `with transaction.atomic():` 块内 — `user_service.py:189` 等自动跳过<br>② `finally` 块内 — 收尾操作<br>③ 行尾 `# noqa: CIMF_W006` — 手动豁免 |
| 告警级别 | `Warning`，id=`CIMF_W006` |

**实现要点：**
- AST 遍历时追踪当前是否在 `With` 节点（且 `context_expr` 为 `transaction.atomic()`）
- 追踪是否在 `TryFinally` 的 `finalbody` 内
- `.save()` 调用通过 `isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "save"` 检测
- 检查 `node.keywords` 中有无 `arg="update_fields"`

### 2. CIMF_W007 — 静默 `except Exception`

| 项目 | 说明 |
|------|------|
| 检测目标 | `core/`、`modules/` 下所有 `.py` 文件 |
| 匹配模式 | `except Exception:` 处理器，body 内无日志调用 |
| 分析方式 | AST 扫描 `ast.Try` 的 `handlers` |
| 豁免条件 | body 内包含 `logger.error()`、`logger.exception()`、`logger.warning()` 之一<br>行尾 `# noqa: CIMF_W007` 或 `# noqa: S110` |
| 告警级别 | `Warning`，id=`CIMF_W007` |

**实现要点：**
- 遍历 handler.body 中的所有 `ast.Call` 节点
- 检查 `func` 是否为 `ast.Attribute` 且 `attr` 为 `error`、`exception`、`warning`
- 同时检查 `func.value` 是否为 `ast.Name(id="logger")`
- 先过滤掉已有的 `# noqa: S110` 行

### 3. 现有 4 处 `# noqa: S110` 补充意图注释

| 文件:行 | 原始代码 | 改为 |
|---------|----------|------|
| `core/checks.py:107` | `except Exception:  # noqa: S110` | `except Exception:  # noqa: S110 — 文件读取/解析异常对检查报告非致命，静默跳过` |
| `core/checks.py:170` | `except Exception:  # noqa: S110` | `except Exception:  # noqa: S110 — AST 解析异常不影响主逻辑` |
| `core/checks.py:233` | `except Exception:  # noqa: S110` | `except Exception:  # noqa: S110 — 同上` |
| `core/checks.py:318` | `except Exception:  # noqa: S110` | `except Exception:  # noqa: S110 — 同上` |

---

## 第二阶段：意图注释（`core/node/services/node_service.py`）

`create_node()` 参数 `_data` 在扫描报告中标记为"被丢弃"，实际为有意设计（动态字段由模块层处理）：

```python
def create_node(node_type_slug: str, _data: dict, user) -> Node | None:
    # _data 由模块层处理，NodeService 仅创建核心节点记录
```

---

## 第三阶段：规范加固（`AGENTS.md`）

### 反模式自查清单新增第 14 项

在现有 13 项末尾追加：

| # | 检查项 | 对应历史 Bug |
|---|--------|-------------|
| 14 | **并发安全？** — 共享资源有无 `threading.Lock` / `select_for_update`？`CronTask.run()` 可重入？| Round 8 |

### 同类问题扩散扫描表新增 3 行

| 发现的问题 | 扩散搜索命令 |
|------------|-------------|
| `save()` 无 `update_fields` | `grep -rn "\.save()" core/ modules/ \| grep -v "update_fields"` |
| 静默 `except Exception` | `manage.py check` 输出中 CIMF_W007 告警 |
| 并发无锁 | `grep -rn "threading\.Lock\|select_for_update" core/ modules/` |

### Bug 排查规范表追加

`服务层检查` 行追加：并发安全、`save(update_fields=...)`

---

## 第四阶段：一键预检查（`run.sh`）

### 新增函数 `run_bug_precheck()`

```bash
run_bug_precheck() {
    echo -e "\n${GREEN}>>> 全面 Bug 预检查${NC}\n"
    activate_venv
    local venv_python
    venv_python=$(get_venv_python)

    # 1) Django 系统检查（含 CIMF_W006/W007）
    echo -e "${CYAN}[1/3] 运行 manage.py check ...${NC}\n"
    $venv_python manage.py check 2>&1

    # 2) save() 无 update_fields 残留扫描
    echo -e "\n${CYAN}[2/3] 扫描 save() 无 update_fields 残留 ...${NC}"
    local results
    results=$(grep -rn "\.save()" core/ modules/ | grep -v "update_fields" | grep -v "# noqa: CIMF_W006" || true)
    if [[ -z "$results" ]]; then
        echo -e "${GREEN}  未发现${NC}"
    else
        echo "$results"
    fi

    # 3) 并发锁覆盖统计
    echo -e "\n${CYAN}[3/3] 并发锁使用概况 ...${NC}"
    echo "$(grep -rn "threading\.Lock" core/ modules/ | wc -l) 处 threading.Lock"
    echo "$(grep -rn "select_for_update" core/ modules/ | wc -l) 处 select_for_update"

    echo -e "\n${GREEN}✅ 预检查完成${NC}"
}
```

### 菜单改动

- `show_maint_menu()` 追加 `echo "  9 → 全面 Bug 预检查 (manage.py check + 增量扫描)"`
- `run_maint_menu()` `read -p` 提示改为 `(0/1/2/3/4/5/6/7/8/9)`
- case 追加 `9) echo "→ 全面 Bug 预检查"; run_bug_precheck ;;`

---

## 执行预估

| # | 内容 | 文件 | 预估时间 |
|---|------|------|:--------:|
| 1 | CIMF_W006 实现（AST 扫描 `.save()`） | `core/checks.py` | 20min |
| 2 | CIMF_W007 实现（AST 扫描静默 except） | `core/checks.py` | 15min |
| 3 | 4 处 `# noqa: S110` 补充意图注释 | `core/checks.py` | 2min |
| 4 | `_data` 参数意图注释 | `core/node/services/node_service.py` | 1min |
| 5 | AGENTS.md 追加第 14 项 + 扩散扫描表 | `AGENTS.md` | 5min |
| 6 | run.sh 选项 9 函数 + 菜单 | `run.sh` | 10min |
| 7 | 验证（check + ruff） | — | 5min |
| | **合计** | **4 个文件** | **~58min** |

---

## 验证步骤

```bash
./venv/bin/python manage.py check           # 确认 CIMF_W006/W007 生效
./venv/bin/ruff check core/ modules/         # 无回归
./venv/bin/python manage.py check_templates  # 模板检查不受影响
git diff --stat                              # 确认变更范围
```

---

## 附录：预防体系全景图

```
┌─────────────────────────────────────────────────────────────┐
│                    Bug 预防体系全景图                        │
├─────────────────────────────────────────────────────────────┤
│  1. 静态分析（Pre-commit）                                   │
│     ├─ Ruff lint + format                                    │
│     ├─ Ruff bandit(S) 规则集                                 │
│     ├─ Ruff DTZ 时区规则集                                   │
│     └─ basedpyright 类型检查                                 │
│                                                             │
│  2. Django 系统检查（manage.py check）                       │
│     ├─ CIMF_W001 — 视图认证装饰器缺失                       │
│     ├─ CIMF_W002 — API 视图 JSON 装饰器缺失                 │
│     ├─ CIMF_W003 — Admin list_select_related N+1            │
│     ├─ CIMF_W004 — Signal handler try/except 缺失           │
│     ├─ CIMF_W005 — 表单对象未传入模板上下文                 │
│     ├─ CIMF_W006 — save() 缺 update_fields       ← 新增    │
│     ├─ CIMF_W007 — 静默 except Exception         ← 新增    │
│     └─ check --deploy — 生产安全配置检查                     │
│                                                             │
│  3. 自定义检查脚本（run.sh 选项）                            │
│     ├─ 选项 6 — Ruff 全量扫描                               │
│     ├─ 选项 7 — Deploy 安全检查                             │
│     ├─ 选项 8 — 模板问题检查 (check_templates)              │
│     └─ 选项 9 — 全面 Bug 预检查                  ← 新增    │
│                                                             │
│  4. 规范文档                                                │
│     ├─ AGENTS.md — 14 项反模式自查清单 + 扩散扫描表         │
│     ├─ docs/技术规范/ — 各层技术规范                        │
│     └─ docs/现有模块.md — 模块索引                          │
└─────────────────────────────────────────────────────────────┘
```
