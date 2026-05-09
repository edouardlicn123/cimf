# -*- coding: utf-8 -*-
"""
===============================================================================
文件：throttling.py
路径：/home/edo/cimf/core/throttling.py
===============================================================================

功能说明：
    自定义请求频率限制类
    
    提供多种频率限制策略：
    - LoginRateThrottle: 登录频率限制 (10/minute)
    - AdminRateThrottle: 管理后台限制 (1000/hour)
    - IPRateThrottle: IP 级别限制 (50/hour)

版本：
    - 1.0: 初始版本

依赖：
    - rest_framework.throttling
"""

from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """登录频率限制：防止暴力破解"""
    scope = 'login'

    def get_cache_key(self, request, view):
        if request.method != 'POST':
            return None
        return self.get_ident(request)


class AdminRateThrottle(SimpleRateThrottle):
    """管理后台频率限制：高权限用户"""
    scope = 'admin'

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None
        if not getattr(request.user, 'is_admin', False):
            return None
        return f"throttle_admin_{request.user.pk}"


class IPRateThrottle(SimpleRateThrottle):
    """IP 级别频率限制：更严格的限制"""
    scope = 'ip'

    def get_cache_key(self, request, view):
        return self.get_ident(request)