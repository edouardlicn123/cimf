"""6 个 Bug 模式检测器

L1（grep）：
  - datetime_now      : datetime.now() 无时区参数
  - jsonfield_default  : JSONField(default={}/[])
  - nullbooleanfield   : NullBooleanField() 弃用

L2（AST）：
  - first_unchecked    : .first() 结果同一函数内使用前未检查 None
  - first_returned     : .first() 结果直接 return
  - save_no_updates    : .save() 无 update_fields
  - modelchoice_static : ModelChoiceField(queryset=...) 非 .none()
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Finding:
    file: str
    line: int
    column: int
    severity: str
    pattern_id: str
    code: str
    message: str
    fix_hint: str


SCAN_DIRS = [
    Path(__file__).parent.parent,  # core/
    Path(__file__).parent.parent.parent / "modules",  # modules/
    Path(__file__).parent.parent.parent / "cimf_django",  # cimf_django/
]

NON_DJANGO_SAVE_CALLERS = frozenset({"wb", "img", "image", "result", "watermarked"})
LINE_CACHE: dict[str, list[str]] = {}


def _get_lines(path: Path) -> list[str]:
    if str(path) not in LINE_CACHE:
        LINE_CACHE[str(path)] = path.read_text(encoding="utf-8").splitlines()
    return LINE_CACHE[str(path)]


def _source_snippet(path: Path, lineno: int, context: int = 1) -> str:
    lines = _get_lines(path)
    start = max(0, lineno - 1 - context)
    end = min(len(lines), lineno - 1 + context + 1)
    return "\n".join(lines[start:end])


# ── L1: grep 检测器 ──────────────────────────────────────────


def detect_datetime_now(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"datetime\.now\(\)", text):
        lineno = text[: m.start()].count("\n") + 1
        findings.append(
            Finding(
                file=str(path),
                line=lineno,
                column=m.start() - text.rfind("\n", 0, m.start()) - 1,
                severity="high",
                pattern_id="datetime_now",
                code=_source_snippet(path, lineno),
                message="datetime.now() 缺少时区参数，应使用 timezone.now()",
                fix_hint="from django.utils import timezone → timezone.now()",
            )
        )
    return findings


def detect_jsonfield_default(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"JSONField\(.*?default\s*=\s*(\{|\[)", text):
        lineno = text[: m.start()].count("\n") + 1
        findings.append(
            Finding(
                file=str(path),
                line=lineno,
                column=m.start() - text.rfind("\n", 0, m.start()) - 1,
                severity="critical",
                pattern_id="jsonfield_default",
                code=_source_snippet(path, lineno),
                message="JSONField 使用可变默认值，所有实例将共享同一对象",
                fix_hint="改为 default=dict 或 default=list（无括号）",
            )
        )
    return findings


def detect_nullbooleanfield(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"NullBooleanField\(", text):
        lineno = text[: m.start()].count("\n") + 1
        findings.append(
            Finding(
                file=str(path),
                line=lineno,
                column=m.start() - text.rfind("\n", 0, m.start()) - 1,
                severity="medium",
                pattern_id="nullbooleanfield",
                code=_source_snippet(path, lineno),
                message="NullBooleanField 已弃用，请使用 TypedChoiceField 或 BooleanField(null=True)",
                fix_hint="TypedChoiceField(choices=[(None,'未知'),(True,'有'),(False,'没有')])",
            )
        )
    return findings


# ── L2: AST 辅助函数 ─────────────────────────────────────────


def _get_call_func_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node.func, ast.Name):
        return node.func.id
    return ""


def _get_call_caller_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
        return node.func.value.id
    return None


def _variable_name_in_expr(var_name: str, node: ast.AST) -> bool:
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and n.id == var_name:
            return True
    return False


def _is_none_check(var_name: str, test_node: ast.AST) -> bool:
    if isinstance(test_node, ast.Name) and test_node.id == var_name:
        return True
    if isinstance(test_node, ast.UnaryOp) and isinstance(test_node.op, ast.Not):
        return _variable_name_in_expr(var_name, test_node.operand)
    if isinstance(test_node, ast.Compare) and len(test_node.ops) == 1:
        op = test_node.ops[0]
        if isinstance(op, (ast.Is, ast.IsNot)):
            for comparator in [test_node.left, *test_node.comparators]:
                if isinstance(comparator, ast.Constant) and comparator.value is None:
                    return _variable_name_in_expr(var_name, test_node.left)
    if isinstance(test_node, ast.BoolOp):
        return any(_is_none_check(var_name, v) for v in test_node.values)
    return False


def _analyze_first_usage(var_name: str, statements: list[ast.stmt], start_idx: int) -> str | None:
    _, result = _walk_for_variable(var_name, statements, start_idx, False)
    return result


def _walk_for_variable(
    var_name: str, statements: list[ast.stmt], start_idx: int, in_checked_block: bool
) -> tuple[bool, str | None]:
    found_none_check = in_checked_block
    for stmt in statements[start_idx:]:
        if isinstance(stmt, ast.If) and _is_none_check(var_name, stmt.test):
            reassigns = _body_reassigns(stmt.body, var_name)
            _, _ = _walk_for_variable(var_name, stmt.body, 0, True)
            if stmt.orelse:
                _, _ = _walk_for_variable(var_name, stmt.orelse, 0, _body_reassigns(stmt.orelse, var_name))
            if _body_exits(stmt.body) or _body_exits(stmt.orelse) or reassigns:
                found_none_check = True
            continue
        if isinstance(stmt, ast.Return) and _variable_name_in_expr(var_name, stmt.value):
            return found_none_check, "returned"
        if isinstance(stmt, ast.Assign):
            for t in stmt.targets:
                if isinstance(t, ast.Name) and t.id == var_name:
                    return found_none_check, None
            if _variable_name_in_expr(var_name, stmt.value):
                if not found_none_check:
                    return found_none_check, "unchecked"
                return found_none_check, None
        if _variable_name_in_expr(var_name, stmt):
            if not found_none_check:
                return found_none_check, "unchecked"
    return found_none_check, None


def _body_exits(body: list[ast.stmt]) -> bool:
    for stmt in body:
        if isinstance(stmt, (ast.Return, ast.Break, ast.Continue, ast.Raise)):
            return True
        if isinstance(stmt, ast.If) and stmt.orelse:
            if _body_exits(stmt.body) and _body_exits(stmt.orelse):
                return True
    return False


def _body_reassigns(body: list[ast.stmt], var_name: str) -> bool:
    for stmt in body:
        if isinstance(stmt, ast.Assign):
            for t in stmt.targets:
                if isinstance(t, ast.Name) and t.id == var_name:
                    return True
        if isinstance(stmt, ast.AugAssign) and isinstance(stmt.target, ast.Name) and stmt.target.id == var_name:
            return True
        if isinstance(stmt, (ast.If, ast.For, ast.While, ast.Try)):
            inner_body = getattr(stmt, "body", [])
            if _body_reassigns(inner_body, var_name):
                return True
            inner_orelse = getattr(stmt, "orelse", [])
            if _body_reassigns(inner_orelse, var_name):
                return True
    return False


# ── L2: AST 检测器 ────────────────────────────────────────────


def detect_first_unchecked_returned(path: Path, tree: ast.AST) -> list[Finding]:
    findings: list[Finding] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if not isinstance(node.value, ast.Call):
                continue
            if _get_call_func_name(node.value) != "first":
                continue
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    continue
                var_name = target.id
                parent_block = _find_parent_block(tree, node)
                if parent_block is None:
                    continue
                stmt_idx = _find_stmt_index(parent_block, node)
                if stmt_idx < 0:
                    continue
                result = _analyze_first_usage(var_name, parent_block, stmt_idx + 1)
                if result == "unchecked":
                    findings.append(
                        Finding(
                            file=str(path),
                            line=node.value.lineno,
                            column=node.value.col_offset,
                            severity="high",
                            pattern_id="first_unchecked",
                            code=_source_snippet(path, node.value.lineno),
                            message=f".first() 结果赋值给 {var_name} 后未检查 None 即使用",  # noqa: CIMF_W008
                            fix_hint=f"添加: if {var_name} is None: return ...",
                        )
                    )
                elif result == "returned":
                    findings.append(
                        Finding(
                            file=str(path),
                            line=node.value.lineno,
                            column=node.value.col_offset,
                            severity="low",
                            pattern_id="first_returned",
                            code=_source_snippet(path, node.value.lineno),
                            message=".first() 结果赋值后直接 return，调用者需检查 None",  # noqa: CIMF_W008
                            fix_hint="调用方应判断返回值是否为 None 后再使用",
                        )
                    )

        elif isinstance(node, ast.Return):
            if not isinstance(node.value, ast.Call):
                continue
            if _get_call_func_name(node.value) != "first":
                continue
            findings.append(
                Finding(
                    file=str(path),
                    line=node.value.lineno,
                    column=node.value.col_offset,
                    severity="low",
                    pattern_id="first_returned",
                    code=_source_snippet(path, node.value.lineno),
                    message="first() 结果直接 return，调用者需检查 None",
                    fix_hint="调用方应判断返回值是否为 None 后再使用",
                )
            )

    return findings


def detect_save_no_update_fields(path: Path, tree: ast.AST) -> list[Finding]:
    findings: list[Finding] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _get_call_func_name(node) != "save":
            continue

        caller = _get_call_caller_name(node)
        if caller and caller in NON_DJANGO_SAVE_CALLERS:
            continue

        has_update_fields = any(
            kw.arg == "update_fields" for kw in node.keywords if isinstance(kw.arg, str)
        )
        if has_update_fields:
            continue

        findings.append(
            Finding(
                file=str(path),
                line=node.lineno,
                column=node.col_offset,
                severity="medium",
                pattern_id="save_no_updates",
                code=_source_snippet(path, node.lineno),
                message=".save() 未指定 update_fields，可能覆盖并发修改",
                fix_hint="添加 update_fields=[...] 仅更新变更字段",
            )
        )
    return findings


def detect_modelchoice_static(path: Path, tree: ast.AST) -> list[Finding]:
    findings: list[Finding] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if not isinstance(item, ast.Assign):
                continue
            if len(item.targets) != 1 or not isinstance(item.targets[0], ast.Name):
                continue
            if not isinstance(item.value, ast.Call):
                continue
            if _get_call_func_name(item.value) != "ModelChoiceField":
                continue
            queryset_kw = None
            for kw in item.value.keywords:
                if isinstance(kw.arg, str) and kw.arg == "queryset":
                    queryset_kw = kw
                    break
            if queryset_kw is None:
                continue
            if _is_none_queryset(queryset_kw.value):
                continue

            findings.append(
                Finding(
                    file=str(path),
                    line=item.lineno,
                    column=item.col_offset,
                    severity="high",
                    pattern_id="modelchoice_static",
                    code=_source_snippet(path, item.lineno),
                    message="ModelChoiceField 使用了静态 queryset，应改为 __init__ 中动态设置",
                    fix_hint="在 __init__ 中设置 self.fields['xxx'].queryset = ...",
                )
            )
    return findings


def _is_none_queryset(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and _get_call_func_name(node) == "none"


def _find_parent_block(tree: ast.AST, target: ast.AST) -> list[ast.stmt] | None:
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(body, list) and target in body:
            return body
        orelse = getattr(node, "orelse", None)
        if isinstance(orelse, list) and target in orelse:
            return orelse
        for attr in ("handlers", "finalbody"):
            handlers = getattr(node, attr, None)
            if isinstance(handlers, list):
                for handler in handlers:
                    h_body = getattr(handler, "body", None)
                    if isinstance(h_body, list) and target in h_body:
                        return h_body
    return None


def _find_stmt_index(body: list[ast.stmt], target: ast.stmt) -> int:
    for i, stmt in enumerate(body):
        if stmt is target:
            return i
    return -1


# ── 统一入口 ──────────────────────────────────────────────────


L1_DETECTORS: list[tuple[str, Any]] = [
    ("datetime_now", detect_datetime_now),
    ("jsonfield_default", detect_jsonfield_default),
    ("nullbooleanfield", detect_nullbooleanfield),
]

L2_DETECTORS: list[tuple[str, Any]] = [
    ("first_unchecked / first_returned", detect_first_unchecked_returned),
    ("save_no_updates", detect_save_no_update_fields),
    ("modelchoice_static", detect_modelchoice_static),
]


def scan_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []

    if path.suffix != ".py":
        return findings

    try:
        text = path.read_text(encoding="utf-8")
    except Exception:  # noqa: CIMF_W007 — file read failure
        return findings

    for pid, detector in L1_DETECTORS:
        try:
            findings.extend(detector(path))
        except Exception:  # noqa: CIMF_W007 — detector failure skip
            pass

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return findings

    for pid, detector in L2_DETECTORS:
        try:
            findings.extend(detector(path, tree))
        except Exception:  # noqa: CIMF_W007 — detector failure skip
            pass

    return findings


def scan_all() -> list[Finding]:
    findings: list[Finding] = []
    scanned = 0
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for f in sorted(scan_dir.rglob("*.py")):
            if "/migrations/" in str(f) or "/__pycache__/" in str(f):
                continue
            scanned += 1
            findings.extend(scan_file(f))
    return findings
