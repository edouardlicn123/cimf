import ast
import logging
import operator

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_POST

from core.constants import ModuleType
from core.decorators import json_body, login_required_json
from core.module.models import Module, ToolType
from core.utils.response import json_error, json_success

logger = logging.getLogger(__name__)


class ArithmeticEvaluator(ast.NodeVisitor):
    """安全算术表达式求值器，不使用 eval"""

    def __init__(self):
        self._ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("不支持的常量类型")

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_func = self._ops.get(type(node.op))
        if not op_func:
            raise ValueError("不支持的运算符")
        return op_func(left, right)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_func = self._ops.get(type(node.op))
        if not op_func:
            raise ValueError("不支持的运算符")
        return op_func(operand)

    def visit_Expression(self, node):
        return self.visit(node.body)

    def generic_visit(self, node):
        raise ValueError(f"不支持的语法: {type(node).__name__}")

    def evaluate(self, expression: str):
        tree = ast.parse(expression.strip(), mode="eval")
        return self.visit(tree)


_evaluator = ArithmeticEvaluator()


@login_required
def tool_view(request):
    """计算器工具页面"""
    tool_type_ids = Module.get_active_ids(ModuleType.TOOL)
    tools = ToolType.objects.filter(slug__in=tool_type_ids, is_active=True)

    return render(
        request,
        "calc/calc.html",
        {
            "tools": tools,
        },
    )


@login_required_json
@require_POST
@json_body
def calculate(request):
    """计算表达式AJAX接口"""
    expression = request.json_data.get("expression", "")

    if not expression:
        return json_error("表达式不能为空")

    allowed_chars = set("0123456789+-*/.() ")
    if not all(c in allowed_chars for c in expression.strip()):
        return json_error("只允许数字和运算符")

    try:
        result = _evaluator.evaluate(expression)
    except ZeroDivisionError:
        return json_error("不能除以零")
    except ValueError as e:
        return json_error(str(e))
    except Exception as e:
        logger.warning(f"表达式求值失败: {e}", exc_info=True)
        return json_error("表达式格式错误")

    return json_success(data={"result": result})
