import ast
import os
from pathlib import Path

from django.core.checks import Warning, register

from .utils import _find_py_files


@register("cimf")
def check_admin_list_select_related(app_configs, **kwargs):  # noqa: ARG001
    errors = []
    admin_dirs = [
        Path(__file__).parent.parent / "node",
        Path(__file__).parent.parent,
        Path(__file__).parent.parent.parent / "modules",
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
        rel_path = os.path.relpath(filepath, Path(__file__).parent.parent)

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
    except Exception:  # noqa: S110
        pass
    return errors
