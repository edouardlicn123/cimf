import ast
import os
from pathlib import Path

from django.core.checks import Warning, register


@register("cimf")
def check_signal_handler_try_except(app_configs, **kwargs):  # noqa: ARG001
    errors = []
    for root, _dirs, files in os.walk(Path(__file__).parent.parent.parent):
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
        rel_path = os.path.relpath(filepath, Path(__file__).parent.parent)
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
    except Exception:  # noqa: S110
        pass
    return errors
