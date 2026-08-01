import ast
from pathlib import Path

from core.bugscan.detectors.ast_utils import (
    _analyze_first_usage,
    _find_parent_block,
    _find_stmt_index,
    _get_call_caller_name,
    _get_call_func_name,
)
from core.bugscan.detectors.finding import NON_DJANGO_SAVE_CALLERS, Finding, _source_snippet


def _is_none_queryset(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and _get_call_func_name(node) == "none"


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


def _has_logger_call(stmts: list[ast.stmt]) -> bool:
    for stmt in stmts:
        for node in ast.walk(stmt):
            if isinstance(node, ast.Call):
                caller = _get_call_caller_name(node)
                if caller in ("logger", "logging"):
                    return True
    return False


def _is_silent_return(stmt: ast.stmt) -> bool:
    if not isinstance(stmt, ast.Return):
        return False
    if stmt.value is None:
        return True
    return isinstance(stmt.value, (ast.Constant, ast.Name, ast.List, ast.Dict, ast.Tuple))


def detect_silent_except(path: Path, tree: ast.AST) -> list[Finding]:
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        for handler in node.handlers:
            if _has_logger_call(handler.body):
                continue
            for stmt in handler.body:
                if isinstance(stmt, (ast.Pass, ast.Continue)) or _is_silent_return(stmt):
                    findings.append(
                        Finding(
                            file=str(path),
                            line=getattr(stmt, "lineno", handler.lineno),
                            column=getattr(stmt, "col_offset", handler.col_offset),
                            severity="medium",
                            pattern_id="silent_except",
                            code=_source_snippet(path, handler.lineno),
                            message="except 块中无日志记录，异常被静默吞没",
                            fix_hint="添加 logger.warning 或 logger.exception(...)",
                        )
                    )
                    break
    return findings


L2_DETECTORS: list[tuple[str, object]] = [
    ("first_unchecked / first_returned", detect_first_unchecked_returned),
    ("save_no_updates", detect_save_no_update_fields),
    ("modelchoice_static", detect_modelchoice_static),
    ("silent_except", detect_silent_except),
]
