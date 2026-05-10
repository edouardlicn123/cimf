# -*- coding: utf-8 -*-
import ast
import operator
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.module.models import Module, ToolType
from core.constants import ModuleType


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
        raise ValueError('不支持的常量类型')

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_func = self._ops.get(type(node.op))
        if not op_func:
            raise ValueError('不支持的运算符')
        return op_func(left, right)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_func = self._ops.get(type(node.op))
        if not op_func:
            raise ValueError('不支持的运算符')
        return op_func(operand)

    def visit_Expression(self, node):
        return self.visit(node.body)

    def evaluate(self, expression: str):
        tree = ast.parse(expression.strip(), mode='eval')
        return self.visit(tree)


_evaluator = ArithmeticEvaluator()


@login_required
def tool_view(request):
    """计算器工具页面"""
    tool_type_ids = Module.objects.filter(
        module_type=ModuleType.TOOL,
        is_active=True
    ).values_list('module_id', flat=True)
    tools = ToolType.objects.filter(slug__in=tool_type_ids, is_active=True)

    return render(request, 'calc/calc.html', {
        'tools': tools,
    })


@login_required
def calculate(request):
    """计算表达式AJAX接口"""
    import json
    from django.http import JsonResponse

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expression = data.get('expression', '')

            if not expression:
                return JsonResponse({'error': '表达式不能为空'}, status=400)

            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression.strip()):
                return JsonResponse({'error': '只允许数字和运算符'}, status=400)

            result = _evaluator.evaluate(expression)

            return JsonResponse({'result': result})
        except ZeroDivisionError:
            return JsonResponse({'error': '不能除以零'}, status=400)
        except Exception:
            return JsonResponse({'error': '表达式格式错误'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
