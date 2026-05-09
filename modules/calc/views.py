# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.module.models import Module, ToolType
from core.constants import ModuleType


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
    import re
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

            result = eval(expression, {"__builtins__": {}}, {"abs": abs, "round": round})

            return JsonResponse({'result': result})
        except ZeroDivisionError:
            return JsonResponse({'error': '不能除以零'}, status=400)
        except Exception as e:
            return JsonResponse({'error': '表达式格式错误'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)