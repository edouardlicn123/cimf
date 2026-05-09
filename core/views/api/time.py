# -*- coding: utf-8 -*-
"""
时间 API 模块
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from core.services import TimeService


@login_required
@require_GET
def api_time_current(request):
    """获取当前时间 API"""
    status = TimeService.get_sync_status()
    synced = status.get('status') == 'success'
    
    return JsonResponse({
        'time': TimeService.get_current_time(),
        'timezone': TimeService.get_timezone(),
        'synced': synced,
    })


@login_required
@require_GET
def api_time_test(request):
    """测试时间服务器连接"""
    from core.services import get_time_sync_service
    time_sync = get_time_sync_service()
    server_url = time_sync.get_server_url()
    server_time = time_sync._fetch_time_from_server(server_url)
    
    return JsonResponse({
        'success': server_time is not None,
        'server': server_url,
        'time': server_time.strftime('%Y-%m-%d %H:%M:%S') if server_time else None,
    })


@login_required
@require_GET
def api_time_status(request):
    """获取时间同步状态"""
    return JsonResponse(TimeService.get_sync_status())