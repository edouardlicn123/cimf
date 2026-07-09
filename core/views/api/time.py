"""
时间 API 模块
"""

from core.decorators import api_get_view
from core.services import TimeService
from core.utils.response import json_success


@api_get_view
def api_time_current(request):  # noqa: ARG001
    """获取当前时间 API"""
    status = TimeService.get_sync_status()
    synced = status.get("status") == "success"

    return json_success(
        {
            "time": TimeService.get_current_time(),
            "timestamp": int(TimeService.get_current_datetime().timestamp()),
            "timezone": TimeService.get_timezone(),
            "synced": synced,
        }
    )


@api_get_view
def api_time_test(request):  # noqa: ARG001
    """测试时间服务器连接"""
    from core.services import get_time_sync_service  # noqa: PLC0415

    time_sync = get_time_sync_service()
    server_url = time_sync.get_server_url()
    server_time = time_sync.test_connection(server_url)

    return json_success(
        extra={
            "success": server_time is not None,
            "server": server_url,
            "time": server_time.strftime("%Y-%m-%d %H:%M:%S") if server_time else None,
        }
    )


@api_get_view
def api_time_status(request):  # noqa: ARG001
    """获取时间同步状态"""
    return json_success(extra=TimeService.get_sync_status())
