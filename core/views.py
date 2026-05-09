# -*- coding: utf-8 -*-
"""
================================================================================
文件：views.py
路径：/home/edo/cimf/core/views.py

功能说明：
    核心应用视图 - 已迁移到 core/views/ 目录
    此文件保留错误处理函数以兼容 settings.py 配置

版本：
    - 2.0: 精简版，仅保留错误处理函数（2026-04-09）

依赖：
    - django: Web 框架
"""

from django.shortcuts import render

# 错误处理函数（保留以兼容 settings.py 配置）
# 实际实现已迁移到 core/views/errors.py


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