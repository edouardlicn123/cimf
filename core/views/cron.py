"""Cron 任务视图模块"""

import logging

from django.shortcuts import render
from django.views.decorators.http import require_POST

from core.decorators import admin_required, admin_required_json, json_body
from core.services import get_cron_service
from core.services.permission_service import get_all_pages_with_permission_status
from core.utils.pagination import paginate_queryset
from core.utils.response import json_success

logger = logging.getLogger(__name__)


@admin_required
def cron_manager(request):
    """Cron 调度管理页面"""
    cron = get_cron_service()

    status = cron.get_status()
    if not status["running"]:
        cron.start()
        status = cron.get_status()

    task_descriptions = {
        "time_sync": "时间同步任务 - 定时与远程时间服务器同步",
        "cache_cleanup": "缓存清理任务 - 清理过期的系统缓存",
    }

    for task in status["tasks"].values():
        task["description"] = task_descriptions.get(task["name"], "未知任务")

    return render(
        request,
        "admin/system_cron_manager.html",
        {
            "cron_status": status,
        },
    )


@admin_required_json
def cron_status(request):  # noqa: ARG001
    """获取 Cron 状态 API"""
    cron = get_cron_service()
    return json_success(extra=cron.get_status())


@admin_required_json
@require_POST
def cron_run_task(request, task_name: str):  # noqa: ARG001
    """手动触发任务"""
    cron = get_cron_service()
    result = cron.trigger(task_name)
    return json_success(extra=result)


@admin_required_json
@require_POST
@json_body
def cron_toggle_task(request, task_name: str):
    """切换任务启用状态"""
    enabled = request.json_data.get("enabled", True)

    cron = get_cron_service()
    result = cron.toggle(task_name, enabled)
    return json_success(extra=result)


@admin_required
def permission_check(request):
    """权限检测页面 - 检测哪些页面需要 admin 权限"""
    filter_status = request.GET.get("filter", "all")

    all_pages = get_all_pages_with_permission_status()

    if filter_status == "restricted":
        pages = [p for p in all_pages if p["has_admin_check"]]
    elif filter_status == "unrestricted":
        pages = [p for p in all_pages if not p["has_admin_check"]]
    else:
        pages = all_pages

    page_obj, page_range = paginate_queryset(request, pages, per_page=20)

    restricted_count = len([p for p in all_pages if p["has_admin_check"]])
    unrestricted_count = len([p for p in all_pages if not p["has_admin_check"]])

    return render(
        request,
        "admin/permission_check.html",
        {
            "page_obj": page_obj,
            "page_range": page_range,
            "filter_status": filter_status,
            "total_count": len(all_pages),
            "restricted_count": restricted_count,
            "unrestricted_count": unrestricted_count,
        },
    )






