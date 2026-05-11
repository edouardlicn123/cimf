"""
Cron 任务视图模块
"""

import inspect
import json
import re

from django.http import JsonResponse
from django.shortcuts import render
from django.urls import get_resolver
from django.views.decorators.http import require_POST

from core.decorators import admin_required
from core.services import get_cron_service
from core.utils.pagination import paginate_queryset


@admin_required
def cron_manager(request):
    """Cron 调度管理页面"""
    cron = get_cron_service()

    status = cron.get_status()
    if not status['running']:
        cron.start()
        status = cron.get_status()

    task_descriptions = {
        'time_sync': '时间同步任务 - 定时与远程时间服务器同步',
        'cache_cleanup': '缓存清理任务 - 清理过期的系统缓存',
    }

    for task in status['tasks'].values():
        task['description'] = task_descriptions.get(task['name'], '未知任务')

    return render(request, 'admin/system_cron_manager.html', {
        'cron_status': status,
        'active_section': 'cron',
    })


@admin_required
def cron_status(request):  # noqa: ARG001
    """获取 Cron 状态 API"""
    cron = get_cron_service()
    return JsonResponse(cron.get_status())


@admin_required
@require_POST
def cron_run_task(request, task_name: str):  # noqa: ARG001
    """手动触发任务"""
    cron = get_cron_service()
    result = cron.trigger(task_name)
    return JsonResponse(result)


@admin_required
@require_POST
def cron_toggle_task(request, task_name: str):
    """切换任务启用状态"""
    try:
        data = json.loads(request.body) if request.body else {}
    except (json.JSONDecodeError, ValueError):
        data = {}
    enabled = data.get('enabled', True)

    cron = get_cron_service()
    result = cron.toggle(task_name, enabled)
    return JsonResponse(result)


@admin_required
def permission_check(request):
    """权限检测页面 - 检测哪些页面需要 admin 权限"""
    filter_status = request.GET.get('filter', 'all')

    all_pages = get_all_pages_with_permission_status()

    if filter_status == 'restricted':
        pages = [p for p in all_pages if p['has_admin_check']]
    elif filter_status == 'unrestricted':
        pages = [p for p in all_pages if not p['has_admin_check']]
    else:
        pages = all_pages

    page_ctx = paginate_queryset(request, pages, per_page=20)

    restricted_count = len([p for p in all_pages if p['has_admin_check']])
    unrestricted_count = len([p for p in all_pages if not p['has_admin_check']])

    return render(request, 'admin/permission_check.html', {
        **page_ctx,
        'filter_status': filter_status,
        'total_count': len(all_pages),
        'restricted_count': restricted_count,
        'unrestricted_count': unrestricted_count,
    })


def get_all_pages_with_permission_status():
    """获取所有页面的权限状态"""
    pages = []
    visited_views = set()

    def extract_patterns(patterns):
        for pattern in patterns:
            if hasattr(pattern, 'url_patterns'):
                extract_patterns(pattern.url_patterns)
            elif hasattr(pattern, 'callback') and pattern.callback:
                view_func = pattern.callback
                view_name = getattr(view_func, '__name__', pattern.name or 'unknown')
                url_pattern = str(pattern.pattern)
                url_pattern = url_pattern.lstrip('^').rstrip('$')

                if not url_pattern or url_pattern == '/':
                    continue

                admin_views = ['changelist_view', 'add_view', 'change_view',
                               'delete_view', 'history_view', 'app_index', 'autocomplete_view',
                               'i18n_javascript', 'password_change', 'password_change_done',
                               'user_change_password', 'catch_all_view', 'view', 'shortcut',
                               'login', 'logout', 'index', 'jsi18n']
                if view_name in admin_views and not pattern.name:
                    continue

                if re.match(r'^\w+/', url_pattern) and not pattern.name:
                    continue

                if url_pattern.endswith(('/add/', '/delete/')):
                    continue

                if view_func in visited_views:
                    continue
                visited_views.add(view_func)

                has_admin_check = False
                source = inspect.getsource(view_func) if callable(view_func) else ''
                if 'PermissionService.can_access_admin' in source or 'is_admin' in source:
                    has_admin_check = True

                pages.append({
                    'name': pattern.name or view_name,
                    'url': url_pattern,
                    'has_admin_check': has_admin_check,
                })

    try:
        resolver = get_resolver()
        extract_patterns(resolver.url_patterns)
    except Exception:
        pass

    return pages


def check_view_has_admin_permission(view_func):
    """检测视图函数是否有 admin 权限检查"""
    try:
        source = inspect.getsource(view_func)
        return 'can_access_admin' in source
    except Exception:
        return False


def detect_app_from_url(url_str):
    """从 URL 检测所属应用"""
    url = url_str.lstrip('/')
    if url.startswith('system/'):
        return 'system'
    elif url.startswith(('nodes/', 'types/', 'type/', 'field-types')):
        return 'nodes'
    elif url.startswith(('taxonomies', 'taxonomy')):
        return 'core'
    elif url.startswith('accounts/'):
        return 'auth'
    elif url.startswith('profile/'):
        return 'profile'
    elif url.startswith('api/'):
        return 'api'
    elif 'node_type_slug' in url_str or 'node_id' in url_str:
        return 'nodes'
    return 'other'
