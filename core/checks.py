"""
自定义 Django 检查：自动检测认证、Admin、Signal、模板表单等常见问题
运行：./venv/bin/python manage.py check
"""

import ast
import os
import re
from pathlib import Path

from django.core.checks import Warning, register

# ── 通用工具函数 ──────────────────────────────────────────────


def _find_py_files(dirs):
    """在多个目录中递归查找 views.py 和 apps.py"""
    for d in dirs:
        d_path = Path(d)
        if not d_path.exists():
            continue
        for root, _dirs, files in os.walk(d):
            if "venv" in root:
                continue
            for f in files:
                if f in ("views.py", "apps.py", "admin.py"):
                    yield Path(root) / f


def _extract_decorators_and_functions(source):
    """从源代码中提取每个公共函数的装饰器列表"""
    func_dec_map = {}
    lines = source.split("\n")
    current_decorators = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("@"):
            deco_match = re.match(r"@(\w+)", stripped)
            if deco_match:
                current_decorators.append(deco_match.group(1))
        elif stripped.startswith("def "):
            func_match = re.match(r"def (\w+)\(", stripped)
            if func_match:
                func_name = func_match.group(1)
                if not func_name.startswith("_"):
                    func_dec_map[func_name] = current_decorators[:]
                current_decorators = []
        elif not stripped.startswith("#"):
            current_decorators = []
    return func_dec_map


# ── Check: 认证装饰器 ─────────────────────────────────────────


@register("cimf")
def check_auth_decorators(app_configs, **kwargs):  # noqa: ARG001
    """检查视图函数是否有认证保护"""
    errors = []
    view_dirs = [
        Path(__file__).parent / "views",
        Path(__file__).parent.parent / "modules",
    ]
    api_decorators = ["login_required_json", "admin_required"]

    for view_dir in view_dirs:
        if not view_dir.exists():
            continue
        for root, _dirs, files in os.walk(view_dir):
            if "venv" in root:
                continue
            for file in files:
                if file == "views.py":
                    filepath = Path(root) / file
                    errors.extend(_check_file_auth(filepath, api_decorators))
    return errors


def _check_file_auth(filepath, api_decorators):
    errors = []
    try:
        with Path(filepath).open() as f:
            content = f.read()
        func_dec_map = _extract_decorators_and_functions(content)
        for func_name, decorators in func_dec_map.items():
            rel_path = os.path.relpath(filepath, Path(__file__).parent)
            if not decorators and not func_name.startswith("api_"):
                errors.append(
                    Warning(
                        f"视图函数 {func_name}() 可能缺少认证装饰器",
                        hint="添加 @login_required 或确保全局中间件已启用",
                        obj=rel_path,
                        id="CIMF_W001",
                    )
                )
                continue
            if func_name.startswith("api_") and not any(d in api_decorators for d in decorators):
                errors.append(
                    Warning(
                        f"API 函数 {func_name}() 应使用 JSON 装饰器",
                        hint="使用 @login_required_json 或 @admin_required",
                        obj=rel_path,
                        id="CIMF_W002",
                    )
                )
    except Exception:  # noqa: S110 — 文件读取/解析异常对检查报告非致命，静默跳过
        pass
    return errors


# ── Check: Admin list_select_related ──────────────────────────


@register("cimf")
def check_admin_list_select_related(app_configs, **kwargs):  # noqa: ARG001
    """检查 ModelAdmin 是否对 FK 字段设置了 list_select_related"""
    errors = []
    admin_dirs = [
        Path(__file__).parent / "node",
        Path(__file__).parent,
        Path(__file__).parent.parent / "modules",
    ]
    for filepath in _find_py_files(admin_dirs):
        if filepath.name != "admin.py":
            continue
        errors.extend(_check_admin_file(filepath))
    return errors


def _check_admin_file(filepath):
    errors = []
    try:
        with Path(filepath).open() as f:
            source = f.read()
        tree = ast.parse(source)
        rel_path = os.path.relpath(filepath, Path(__file__).parent)

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            if not any("Admin" in b for b in bases):
                continue

            list_display = None
            has_select_related = False
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            if target.id == "list_display" and isinstance(item.value, ast.List):
                                list_display = [e.value for e in item.value.elts if isinstance(e, ast.Constant)]
                            elif target.id == "list_select_related":
                                has_select_related = True

            if list_display is None:
                continue

            fk_fields = [f for f in list_display if isinstance(f, str) and f.endswith("_id") and f != "id"]
            if fk_fields and not has_select_related:
                errors.append(
                    Warning(
                        f"{node.name}.list_display 含外键字段 {fk_fields} 但未设置 list_select_related（潜在 N+1）",
                        hint=f"添加 list_select_related = [{', '.join(repr(f[:-3]) for f in fk_fields)}]",
                        obj=f"{rel_path}:{node.lineno}",
                        id="CIMF_W003",
                    )
                )
    except Exception:  # noqa: S110 — AST 解析异常不影响主逻辑
        pass
    return errors


# ── Check: Signal handler try/except ──────────────────────────


@register("cimf")
def check_signal_handler_try_except(app_configs, **kwargs):  # noqa: ARG001
    """检查 AppConfig.ready() 中信号连接的回调函数是否包 try/except"""
    errors = []
    for root, _dirs, files in os.walk(Path(__file__).parent.parent):
        if "venv" in root:
            continue
        for f in files:
            if f == "apps.py":
                filepath = Path(root) / f
                errors.extend(_check_apps_file(filepath))
    return errors


def _check_apps_file(filepath):
    errors = []
    try:
        with Path(filepath).open() as f:
            source = f.read()
        tree = ast.parse(source)
        rel_path = os.path.relpath(filepath, Path(__file__).parent)
        ready_methods = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "ready"]
        for ready_node in ready_methods:
            handler_names = set()
            for stmt in ast.walk(ready_node):
                if isinstance(stmt, ast.Call):
                    func = stmt.func
                    if isinstance(func, ast.Attribute) and func.attr == "connect" and stmt.args:
                        handler_name = None
                        if isinstance(stmt.args[0], ast.Name):
                            handler_name = stmt.args[0].id
                        elif isinstance(stmt.args[0], ast.Lambda):
                            continue
                        if handler_name:
                            handler_names.add(handler_name)

            for hname in handler_names:
                handler_funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == hname]
                for hf in handler_funcs:
                    has_try = any(isinstance(s, ast.Try) for s in hf.body)
                    if not has_try:
                        errors.append(
                            Warning(
                                f"信号处理函数 {hname}() 缺少 try/except 保护",
                                hint="在函数体内添加 try/except 包裹可能失败的逻辑",
                                obj=f"{rel_path}:{hf.lineno}",
                                id="CIMF_W004",
                            )
                        )
    except Exception:  # noqa: S110 — AST 解析异常不影响主逻辑
        pass
    return errors


# ── Check: 表单对象传入模板 ──────────────────────────────────


@register("cimf")
def check_form_in_template(app_configs, **kwargs):  # noqa: ARG001
    """检查带表单的视图是否将 form 对象传入模板上下文"""
    errors = []
    view_dirs = [
        Path(__file__).parent / "views",
        Path(__file__).parent.parent / "modules",
    ]
    form_import_pattern = re.compile(
        r"(LoginForm|ProfileForm|PreferencesForm|ChangePasswordForm|SystemSettingsForm|UserCreateForm|UserEditForm|UserSearchForm)"
    )

    for view_dir in view_dirs:
        if not view_dir.exists():
            continue
        for root, _dirs, files in os.walk(view_dir):
            if "venv" in root:
                continue
            for file in files:
                if file == "views.py":
                    filepath = Path(root) / file
                    errors.extend(_check_view_file_form(filepath, form_import_pattern))
    return errors


def _check_view_file_form(filepath, form_import_pattern):
    errors = []
    try:
        with Path(filepath).open() as f:
            source = f.read()
        if not form_import_pattern.search(source):
            return errors
        tree = ast.parse(source)
        rel_path = os.path.relpath(filepath, Path(__file__).parent)

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) or node.name.startswith("_"):
                continue
            # ignore pure-API views
            if node.name.startswith("api_"):
                continue

            has_form_var = False
            has_render = False
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name) and target.id in (
                            "form",
                            "login_form",
                            "user_form",
                            "setting_form",
                        ):
                            has_form_var = True
                if isinstance(stmt, ast.Call):
                    func = stmt.func
                    if isinstance(func, ast.Name) and func.id == "render":
                        has_render = True

            if has_form_var and has_render:
                context_arg = None
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Call):
                        func = stmt.func
                        if isinstance(func, ast.Name) and func.id == "render" and len(stmt.args) >= 3:
                            context_arg = stmt.args[2]
                            break
                if context_arg is not None and isinstance(context_arg, ast.Dict):
                    form_in_context = any(
                        isinstance(k, ast.Constant) and k.value in ("form",) for k in context_arg.keys
                    )
                    if not form_in_context:
                        errors.append(
                            Warning(
                                f"视图 {node.name}() 使用了表单变量但未将 'form' 传入模板上下文",
                                hint="向 render() 的 context dict 添加 'form' 键",
                                obj=f"{rel_path}:{node.lineno}",
                                id="CIMF_W005",
                            )
                        )
    except Exception:  # noqa: S110 — AST 解析异常不影响主逻辑
        pass
    return errors


# ── 通用：递归查找所有 .py 文件 ──────────────────────────────


def _find_all_py_files(dirs):
    """在多个目录中递归查找所有 .py 文件"""
    for d in dirs:
        d_path = Path(d)
        if not d_path.exists():
            continue
        for root, _dirs, files in os.walk(d_path):
            if "venv" in root or "__pycache__" in root or "migrations" in root:
                continue
            for f in files:
                if f.endswith(".py"):
                    yield Path(root) / f


# ── Check: save() 缺 update_fields ────────────────────────────


def _is_in_transaction_atomic(node):
    """检查 AST 节点是否在 with transaction.atomic() 块内"""
    parent = getattr(node, "parent", None)
    while parent is not None:
        if isinstance(parent, ast.With):
            for item in parent.items:
                if isinstance(item.context_expr, ast.Call):
                    func = item.context_expr.func
                    if isinstance(func, ast.Attribute) and func.attr == "atomic":
                        return True
                    if isinstance(func, ast.Name) and func.id == "atomic":
                        return True
        parent = getattr(parent, "parent", None)
    return False


def _is_in_finally_block(node):
    """检查 AST 节点是否在 try/finally 的 finally 块内"""
    parent = getattr(node, "parent", None)
    while parent is not None:
        if isinstance(parent, ast.Try) and node in parent.finalbody:
            return True
        parent = getattr(parent, "parent", None)
    return False


def _has_update_fields_keyword(call_node):
    """检查 .save() 调用是否包含 update_fields 关键字参数"""
    return any(kw.arg == "update_fields" for kw in call_node.keywords)


def _attach_parents(tree):
    """为 AST 树的所有节点添加 parent 引用"""
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node


@register("cimf")
def check_save_update_fields(app_configs, **kwargs):  # noqa: ARG001
    """检查 .save() 调用是否显式指定 update_fields，避免全字段更新"""
    errors = []
    scan_dirs = [
        Path(__file__).parent,
        Path(__file__).parent.parent / "modules",
    ]
    for filepath in _find_all_py_files(scan_dirs):
        try:
            with filepath.open(encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
            _attach_parents(tree)
            rel_path = os.path.relpath(filepath, Path(__file__).parent)
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


# ── Check: 静默 except Exception ──────────────────────────────


@register("cimf")
def check_silent_except(app_configs, **kwargs):  # noqa: ARG001
    """检查 except Exception 处理器是否包含日志输出"""
    errors = []
    scan_dirs = [
        Path(__file__).parent,
        Path(__file__).parent.parent / "modules",
    ]
    for filepath in _find_all_py_files(scan_dirs):
        try:
            with filepath.open(encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
            rel_path = os.path.relpath(filepath, Path(__file__).parent)
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


# ── Check: .first() 未检查 None ─────────────────────────────


@register("cimf")
def check_first_no_none_check(app_configs, **kwargs):  # noqa: ARG001
    """检查 .first() 返回值是否在后续使用前做了 None 检查"""
    errors = []
    scan_dirs = [
        Path(__file__).parent,
        Path(__file__).parent.parent / "modules",
    ]
    first_assign_re = re.compile(r"^(\s*)(\w+)\s*=\s*(.+)\.first\(\)")

    for filepath in _find_all_py_files(scan_dirs):
        try:
            with filepath.open(encoding="utf-8") as f:
                source = f.read()
            source_lines = source.split("\n")
            rel_path = os.path.relpath(filepath, Path(__file__).parent)

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


# ── Check: mark_safe / |safe ────────────────────────────────


@register("cimf")
def check_mark_safe_usage(app_configs, **kwargs):  # noqa: ARG001
    """检查 mark_safe / |safe 的滥用风险"""
    errors = []
    scan_dirs = [
        Path(__file__).parent,
        Path(__file__).parent.parent / "modules",
    ]
    mark_safe_re = re.compile(r"\bmark_safe\(")

    for filepath in _find_all_py_files(scan_dirs):
        try:
            with filepath.open(encoding="utf-8") as f:
                source = f.read()
            source_lines = source.split("\n")
            rel_path = os.path.relpath(filepath, Path(__file__).parent)

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


# ── Check: ModelChoiceField 静态 queryset ────────────────────


@register("cimf")
def check_model_choice_field_queryset(app_configs, **kwargs):  # noqa: ARG001
    """检查 ModelChoiceField 的 queryset 是否在类加载时评估（应为实例化时动态设置）"""
    errors = []
    scan_dirs = [
        Path(__file__).parent,
        Path(__file__).parent.parent / "modules",
    ]
    for filepath in _find_all_py_files(scan_dirs):
        if filepath.name != "forms.py":
            continue
        try:
            with filepath.open(encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
            rel_path = os.path.relpath(filepath, Path(__file__).parent)
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
                                if isinstance(kw.value, ast.Call) and isinstance(kw.value.func, ast.Attribute):
                                    if kw.value.func.attr == "none":
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


# ── Check: NullBooleanField ──────────────────────────────────


@register("cimf")
def check_null_boolean_field(app_configs, **kwargs):  # noqa: ARG001
    """检查是否使用了已弃用的 NullBooleanField（Django 4.0+）"""
    errors = []
    scan_dirs = [
        Path(__file__).parent,
        Path(__file__).parent.parent / "modules",
    ]
    null_boolean_re = re.compile(r"\bNullBooleanField\(")

    for filepath in _find_all_py_files(scan_dirs):
        if filepath.name != "forms.py":
            continue
        try:
            with filepath.open(encoding="utf-8") as f:
                source = f.read()
            source_lines = source.split("\n")
            rel_path = os.path.relpath(filepath, Path(__file__).parent)

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
