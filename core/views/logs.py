"""
日志管理视图
"""

from django.http import JsonResponse
from django.shortcuts import redirect, render

from core.decorators import admin_required
from core.services.log_service import LogService
from core.utils.response import json_error


def _parse_page_params(request, default_page=1, default_size=100):
    try:
        page = int(request.GET.get("page", default_page))
        page_size = int(request.GET.get("page_size", default_size))
    except (ValueError, TypeError):
        page = default_page
        page_size = default_size
    return page, page_size


@admin_required
def logs_index(request):  # noqa: ARG001
    """日志管理首页 - 默认显示 cimf 日志"""
    return redirect("core:logs_view", log_type="cimf")


@admin_required
def logs_view(request, log_type):
    """查看指定日志 - 分页显示日志内容"""
    page, page_size = _parse_page_params(request)
    level = request.GET.get("level", "all")

    if log_type not in ["cimf", "error", "security"]:
        log_type = "cimf"

    log_data = LogService.read_log(log_type, page, page_size, level)
    log_files = LogService.get_log_files()
    stats = LogService.get_log_stats(log_type)

    return render(
        request,
        "admin/logs.html",
        {
            "log_type": log_type,
            "log_files": log_files,
            "log_data": log_data,
            "stats": stats,
            "current_level": level,
        },
    )


# TODO: logs_api 已定义但未注册路由，预留用于前端 AJAX 日志加载功能
@admin_required
def logs_api(request, log_type):
    """日志 API - JSON 接口（未注册路由，预留功能）"""
    page, page_size = _parse_page_params(request)
    level = request.GET.get("level", "all")

    if log_type not in ["cimf", "error", "security"]:
        return json_error("Invalid log type", 400)

    log_data = LogService.read_log(log_type, page, page_size, level)
    return JsonResponse(log_data)
