import ast
import os
import re
from pathlib import Path

from django.core.checks import Warning, register


@register("cimf")
def check_form_in_template(app_configs, **kwargs):  # noqa: ARG001
    errors = []
    view_dirs = [
        Path(__file__).parent.parent / "views",
        Path(__file__).parent.parent.parent / "modules",
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
        rel_path = os.path.relpath(filepath, Path(__file__).parent.parent)

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) or node.name.startswith("_"):
                continue
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
    except Exception:  # noqa: S110
        pass
    return errors
