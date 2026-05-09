# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .services import ClockService
from core.decorators import login_required_json


@require_http_methods(["GET"])
@login_required_json
def api_time(request):
    """获取当前时间 API"""
    return JsonResponse({
        'success': True,
        'data': ClockService.get_current_time(),
    })
