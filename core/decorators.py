# -*- coding: utf-8 -*-
"""
权限检查装饰器模块
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


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
        from core.services import PermissionService
        if not PermissionService.can_access_admin(request.user):
            messages.error(request, '需要系统管理员权限访问该页面')
            return redirect('core:dashboard')
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
            from core.services import PermissionService
            if not PermissionService.has_permission(request.user, permission):
                messages.error(request, '您没有权限访问该页面')
                return redirect('core:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def login_required_json(func):
    """登录Required装饰器，返回JSON错误"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': '请先登录'}, status=401)
        return func(request, *args, **kwargs)
    return wrapper