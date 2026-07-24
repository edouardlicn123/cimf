from django.views.decorators.http import require_http_methods

from core.decorators import login_required_json
from core.utils.response import json_success

from .services import ClockService


@require_http_methods(["GET"])
@login_required_json
def api_time(request):  # noqa: ARG001
    """获取当前时间 API"""
    return json_success(data=ClockService.get_current_time())
