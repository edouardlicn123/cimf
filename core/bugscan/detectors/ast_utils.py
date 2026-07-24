import ast


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
    return any(isinstance(n, ast.Name) and n.id == var_name for n in ast.walk(node))


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
        if _variable_name_in_expr(var_name, stmt) and not found_none_check:
            return found_none_check, "unchecked"
    return found_none_check, None


def _body_exits(body: list[ast.stmt]) -> bool:
    for stmt in body:
        if isinstance(stmt, (ast.Return, ast.Break, ast.Continue, ast.Raise)):
            return True
        if isinstance(stmt, ast.If) and stmt.orelse and _body_exits(stmt.body) and _body_exits(stmt.orelse):
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
