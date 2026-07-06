"""
权限检查装饰器模块
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_GET, require_POST

from core.utils.response import json_error


def admin_required(view_func):
    """
    管理员权限检查装饰器

    检查用户是否具有系统管理员权限，如果没有则重定向到仪表盘并显示错误消息。

    用法：
        @admin_required
        def my_view(request):
            ...
    """

    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from core.services import PermissionService  # noqa: PLC0415

        if not PermissionService.can_access_admin(request.user):
            messages.error(request, "需要系统管理员权限访问该页面")
            return redirect("core:dashboard")
        return view_func(request, *args, **kwargs)

    return wrapper


def permission_required(permission: str):
    """
    权限检查装饰器（指定具体权限）

    Args:
        permission: 权限标识符，如 'import.view'

    用法：
        @permission_required('import.view')
        def my_view(request):
            ...
    """

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            from core.services import PermissionService  # noqa: PLC0415

            if not PermissionService.has_permission(request.user, permission):
                messages.error(request, "您没有权限访问该页面")
                return redirect("core:dashboard")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def api_get_view(view_func):
    return login_required(require_GET(view_func))


def api_post_view(view_func):
    return login_required(require_POST(view_func))


def admin_post_view(view_func):
    return admin_required(require_POST(view_func))


def login_required_json(func):
    """登录Required装饰器，返回JSON错误"""

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return json_error("请先登录", 401)
        return func(request, *args, **kwargs)

    return wrapper


def admin_required_json(view_func):
    """管理员权限检查装饰器，返回JSON错误（用于API）"""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return json_error("请先登录", 401)
        if not getattr(request.user, "is_admin", False):
            return json_error("需要管理员权限", 403)
        return view_func(request, *args, **kwargs)

    return wrapper


def handle_form_errors(view_func):
    """捕获 ValueError 并转为 messages.error + redirect"""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except ValueError as e:
            messages.error(request, str(e))
            if request.method == "POST":
                return redirect(request.path)
            return redirect("core:dashboard")

    return wrapper
