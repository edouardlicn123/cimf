# -*- coding: utf-8 -*-
"""
错误处理视图模块
"""

from django.shortcuts import render


def error_400(request, exception):
    """400 - 错误请求"""
    return render(request, 'errors/400.html', {
        'exception': exception,
    }, status=400)


def error_403(request, exception):
    """403 - 无权限"""
    return render(request, 'errors/403.html', {
        'exception': exception,
    }, status=403)


def error_404(request, exception):
    """404 - 页面未找到"""
    return render(request, 'errors/404.html', {
        'exception': exception,
    }, status=404)


def error_500(request):
    """500 - 服务器错误"""
    return render(request, 'errors/500.html', {
        'exception': None,
    }, status=500)