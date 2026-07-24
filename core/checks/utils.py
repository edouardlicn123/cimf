import ast
import os
import re
from pathlib import Path


def _find_py_files(dirs):
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


def _find_all_py_files(dirs):
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


def _is_in_transaction_atomic(node):
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
    parent = getattr(node, "parent", None)
    while parent is not None:
        if isinstance(parent, ast.Try) and node in parent.finalbody:
            return True
        parent = getattr(parent, "parent", None)
    return False


def _has_update_fields_keyword(call_node):
    return any(kw.arg == "update_fields" for kw in call_node.keywords)


def _attach_parents(tree):
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
