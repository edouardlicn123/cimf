import os
from pathlib import Path

from django.core.checks import Warning, register

from .utils import _extract_decorators_and_functions


@register("cimf")
def check_auth_decorators(app_configs, **kwargs):  # noqa: ARG001
    errors = []
    view_dirs = [
        Path(__file__).parent.parent / "views",
        Path(__file__).parent.parent.parent / "modules",
    ]
    api_decorators = ["login_required_json", "admin_required", "admin_required_json"]

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
            rel_path = os.path.relpath(filepath, Path(__file__).parent.parent)
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
    except Exception:  # noqa: S110
        pass
    return errors
