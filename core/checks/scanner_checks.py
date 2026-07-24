import ast
import os
import re
from pathlib import Path

from django.core.checks import Warning, register

from .utils import (
    _attach_parents,
    _find_all_py_files,
    _has_update_fields_keyword,
    _is_in_finally_block,
    _is_in_transaction_atomic,
)


@register("cimf")
def check_save_update_fields(app_configs, **kwargs):  # noqa: ARG001
    errors = []
    scan_dirs = [
        Path(__file__).parent.parent,
        Path(__file__).parent.parent.parent / "modules",
    ]
    for filepath in _find_all_py_files(scan_dirs):
        try:
            with filepath.open(encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
            _attach_parents(tree)
            rel_path = os.path.relpath(filepath, Path(__file__).parent.parent)
            source_lines = source.split("\n")

            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if not isinstance(node.func, ast.Attribute) or node.func.attr != "save":
                    continue
                if _has_update_fields_keyword(node):
                    continue
                if _is_in_finally_block(node):
                    continue
                if _is_in_transaction_atomic(node):
                    continue
                lineno = getattr(node, "lineno", 0)
                if lineno > 0 and lineno <= len(source_lines):
                    line_text = source_lines[lineno - 1]
                    if "# noqa: CIMF_W006" in line_text:
                        continue
                errors.append(
                    Warning(
                        f"{filepath.name} 第 {lineno} 行: .save() 未指定 update_fields",
                        hint="添加 update_fields=[...] 明确指定更新字段，避免全字段更新",
                        obj=f"{rel_path}:{lineno}",
                        id="CIMF_W006",
                    )
                )
        except SyntaxError:
            pass
    return errors


@register("cimf")
def check_silent_except(app_configs, **kwargs):  # noqa: ARG001
    errors = []
    scan_dirs = [
        Path(__file__).parent.parent,
        Path(__file__).parent.parent.parent / "modules",
    ]
    for filepath in _find_all_py_files(scan_dirs):
        try:
            with filepath.open(encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
            rel_path = os.path.relpath(filepath, Path(__file__).parent.parent)
            source_lines = source.split("\n")

            for try_node in ast.walk(tree):
                if not isinstance(try_node, ast.Try):
                    continue
                for handler in try_node.handlers:
                    if handler.type is None:
                        continue
                    if not (isinstance(handler.type, ast.Name) and handler.type.id == "Exception"):
                        continue
                    lineno = getattr(handler, "lineno", 0)
                    if lineno > 0 and lineno <= len(source_lines):
                        line_text = source_lines[lineno - 1]
                        if "# noqa: CIMF_W007" in line_text or "# noqa: S110" in line_text:
                            continue
                    has_logger = False
                    for stmt in ast.walk(handler):
                        if (
                            isinstance(stmt, ast.Call)
                            and isinstance(stmt.func, ast.Attribute)
                            and stmt.func.attr in ("error", "exception", "warning")
                            and isinstance(stmt.func.value, ast.Name)
                            and stmt.func.value.id == "logger"
                        ):
                            has_logger = True
                            break
                    if not has_logger:
                        errors.append(
                            Warning(
                                f"{filepath.name} 第 {lineno} 行: except Exception 静默处理，缺少日志记录",
                                hint="添加 logger.error/exception/warning 记录异常信息，或加 # noqa: CIMF_W007 注明意图",
                                obj=f"{rel_path}:{lineno}",
                                id="CIMF_W007",
                            )
                        )
        except SyntaxError:
            pass
    return errors


@register("cimf")
def check_first_no_none_check(app_configs, **kwargs):  # noqa: ARG001
    errors = []
    scan_dirs = [
        Path(__file__).parent.parent,
        Path(__file__).parent.parent.parent / "modules",
    ]
    first_assign_re = re.compile(r"^(\s*)(\w+)\s*=\s*(.+)\.first\(\)")

    for filepath in _find_all_py_files(scan_dirs):
        try:
            with filepath.open(encoding="utf-8") as f:
                source = f.read()
            source_lines = source.split("\n")
            rel_path = os.path.relpath(filepath, Path(__file__).parent.parent)

            for i, line in enumerate(source_lines):
                m = first_assign_re.match(line)
                if not m:
                    continue
                var_name = m.group(2)
                if "# noqa: CIMF_W008" in line:
                    continue

                found_check = False
                for j in range(i + 1, min(i + 12, len(source_lines))):
                    cline = source_lines[j].strip()
                    if re.search(
                        rf"if\s+{re.escape(var_name)}(\s+is\s+None|\s+is\s+not\s+None|\s*:|\b)",
                        cline,
                    ) or re.search(rf"if\s+not\s+{re.escape(var_name)}\b", cline):
                        found_check = True
                        break
                    if cline and not cline.startswith("#") and not cline.startswith("assert "):
                        pass

                if not found_check:
                    errors.append(
                        Warning(
                            f"{filepath.name} 第 {i + 1} 行: .first() 返回值 {var_name} 使用前未检查 None",
                            hint=f"添加 'if {var_name} is None' 守卫检查，或加 # noqa: CIMF_W008",
                            obj=f"{rel_path}:{i + 1}",
                            id="CIMF_W008",
                        )
                    )
        except SyntaxError:
            pass
    return errors


@register("cimf")
def check_mark_safe_usage(app_configs, **kwargs):  # noqa: ARG001
    errors = []
    scan_dirs = [
        Path(__file__).parent.parent,
        Path(__file__).parent.parent.parent / "modules",
    ]
    mark_safe_re = re.compile(r"\bmark_safe\(")  # noqa: CIMF_W009

    for filepath in _find_all_py_files(scan_dirs):
        try:
            with filepath.open(encoding="utf-8") as f:
                source = f.read()
            source_lines = source.split("\n")
            rel_path = os.path.relpath(filepath, Path(__file__).parent.parent)

            for i, line in enumerate(source_lines):
                if not mark_safe_re.search(line):
                    continue
                if "# noqa: CIMF_W009" in line:
                    continue
                    errors.append(
                        Warning(
                            f"{filepath.name} 第 {i + 1} 行: mark_safe() 使用，需确认已转义用户输入",  # noqa: CIMF_W009
                            hint="确保传入 mark_safe 的内容不含用户可控的 HTML，或加 # noqa: CIMF_W009 注明理由",  # noqa: CIMF_W009
                            obj=f"{rel_path}:{i + 1}",
                            id="CIMF_W009",
                        )
                )
        except SyntaxError:
            pass

    try:
        from django.conf import settings  # noqa: PLC0415
    except Exception:  # noqa: CIMF_W007
        return errors

    for template_conf in getattr(settings, "TEMPLATES", []):
        if "Jinja2" not in template_conf.get("BACKEND", ""):
            continue
        for tpl_dir in template_conf.get("DIRS", []):
            tpl_path = Path(tpl_dir)
            if not tpl_path.exists():
                continue
            for html_file in tpl_path.rglob("*.html"):
                try:
                    content = html_file.read_text(encoding="utf-8")
                    lines = content.split("\n")
                    rel = str(html_file.relative_to(tpl_path))
                    for i, line in enumerate(lines):
                        if "|safe" not in line:
                            continue
                        if "# noqa: CIMF_W009" in line:
                            continue
                        errors.append(
                            Warning(
                                f"{rel} 第 {i + 1} 行: 使用了 |safe 过滤器",
                                hint="确认内容已转义用户输入，或加 {# noqa: CIMF_W009 #} 注明理由",
                                obj=f"{rel}:{i + 1}",
                                id="CIMF_W009",
                            )
                        )
                except Exception:  # noqa: S110
                    pass
    return errors


@register("cimf")
def check_model_choice_field_queryset(app_configs, **kwargs):  # noqa: ARG001
    errors = []
    scan_dirs = [
        Path(__file__).parent.parent,
        Path(__file__).parent.parent.parent / "modules",
    ]
    for filepath in _find_all_py_files(scan_dirs):
        if filepath.name != "forms.py":
            continue
        try:
            with filepath.open(encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
            rel_path = os.path.relpath(filepath, Path(__file__).parent.parent)
            source_lines = source.split("\n")

            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                if not any(isinstance(b, ast.Name) and "Form" in b.id for b in node.bases):
                    continue
                for item in node.body:
                    if not isinstance(item, ast.Assign):
                        continue
                    for target in item.targets:
                        if not isinstance(target, ast.Name):
                            continue
                        if not isinstance(item.value, ast.Call):
                            continue
                        call = item.value
                        if not isinstance(call.func, ast.Attribute):
                            continue
                        if call.func.attr not in ("ModelChoiceField", "ModelMultipleChoiceField"):
                            continue
                        has_queryset_kw = False
                        queryset_is_none = False
                        for kw in call.keywords:
                            if kw.arg == "queryset":
                                has_queryset_kw = True
                                if isinstance(kw.value, ast.Call) and isinstance(kw.value.func, ast.Attribute) and kw.value.func.attr == "none":
                                    queryset_is_none = True
                        if has_queryset_kw and not queryset_is_none:
                            lineno = getattr(item, "lineno", 0)
                            if lineno > 0 and lineno <= len(source_lines):
                                line_text = source_lines[lineno - 1]
                                if "# noqa: CIMF_W010" in line_text:
                                    continue
                            errors.append(
                                Warning(
                                    f"{filepath.name} 第 {lineno} 行: {target.id} 的 queryset 在类加载时评估",
                                    hint="将 queryset=... 移到 __init__ 中动态赋值，防止数据陈旧",
                                    obj=f"{rel_path}:{lineno}",
                                    id="CIMF_W010",
                                )
                            )
        except SyntaxError:
            pass
    return errors


@register("cimf")
def check_null_boolean_field(app_configs, **kwargs):  # noqa: ARG001
    errors = []
    scan_dirs = [
        Path(__file__).parent.parent,
        Path(__file__).parent.parent.parent / "modules",
    ]
    null_boolean_re = re.compile(r"\bNullBooleanField\(")

    for filepath in _find_all_py_files(scan_dirs):
        if filepath.name != "forms.py":
            continue
        try:
            with filepath.open(encoding="utf-8") as f:
                source = f.read()
            source_lines = source.split("\n")
            rel_path = os.path.relpath(filepath, Path(__file__).parent.parent)

            for i, line in enumerate(source_lines):
                if not null_boolean_re.search(line):
                    continue
                if "# noqa: CIMF_W011" in line:
                    continue
                errors.append(
                    Warning(
                        f"{filepath.name} 第 {i + 1} 行: NullBooleanField 已弃用（Django 4.0+）",
                        hint="替换为 TypedChoiceField(choices=[(None,'未检测'),(True,'有'),(False,'没有')]) 或 BooleanField(null=True)",
                        obj=f"{rel_path}:{i + 1}",
                        id="CIMF_W011",
                    )
                )
        except SyntaxError:
            pass
    return errors
