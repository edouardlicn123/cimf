"""
时间 API 模块
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from core.services import TimeService


@login_required
@require_GET
def api_time_current(request):  # noqa: ARG001
    """获取当前时间 API"""
    status = TimeService.get_sync_status()
    synced = status.get('status') == 'success'

    return JsonResponse({
        'time': TimeService.get_current_time(),
        'timestamp': int(TimeService.get_current_datetime().timestamp()),
        'timezone': TimeService.get_timezone(),
        'synced': synced,
    })


@login_required
@require_GET
def api_time_test(request):  # noqa: ARG001
    """测试时间服务器连接"""
    from core.services import get_time_sync_service  # noqa: PLC0415
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
def api_time_status(request):  # noqa: ARG001
    """获取时间同步状态"""
    return JsonResponse(TimeService.get_sync_status())
