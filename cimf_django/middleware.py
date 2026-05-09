# -*- coding: utf-8 -*-
"""
IP 访问限制中间件
"""

import ipaddress
import logging
from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger('cimf')


class IPWhitelistMiddleware:
    """IP白名单中间件"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'IP_RESTRICTION_ENABLED', False)
        self.whitelist = getattr(settings, 'IP_WHITELIST', [])
        self._compiled_whitelist = []

        for ip_str in self.whitelist:
            try:
                if '/' in ip_str:
                    self._compiled_whitelist.append(
                        ipaddress.ip_network(ip_str, strict=False)
                    )
                else:
                    self._compiled_whitelist.append(
                        ipaddress.ip_address(ip_str)
                    )
            except ValueError:
                logger.warning(f"无效的IP配置: {ip_str}")

    def __call__(self, request):
        if not self.enabled:
            return self.get_response(request)

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0].strip()
        else:
            client_ip = request.META.get('REMOTE_ADDR', '')

        if not self._is_ip_allowed(client_ip):
            logger.warning(
                f"IP访问被拒绝: {client_ip} - {request.method} {request.path} - "
                f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
            )
            if 'application/json' in request.headers.get('Accept', ''):
                return JsonResponse({'error': '拒绝访问：您的IP不在允许范围内'}, status=403)
            from django.http import HttpResponse
            return HttpResponse('<h1>403 Forbidden</h1><p>拒绝访问：您的IP不在允许范围内</p>', status=403)

        return self.get_response(request)

    def _is_ip_allowed(self, client_ip):
        try:
            client_addr = ipaddress.ip_address(client_ip)
            for item in self._compiled_whitelist:
                if isinstance(item, ipaddress.IPv4Network):
                    if client_addr in item:
                        return True
                else:
                    if client_addr == item:
                        return True
            return False
        except ValueError:
            return False


class GlobalLoginRequiredMiddleware:
    """全局登录要求中间件 - 一次性解决认证遗漏问题"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 白名单：不需要登录的路径
        self.whitelist = [
            '/accounts/login/',
            '/admin/login/',
            '/api/',  # API 有自己的认证装饰器
        ]
    
    def __call__(self, request):
        # 检查是否在白名单
        if any(request.path.startswith(url) for url in self.whitelist):
            return self.get_response(request)
        
        # 已登录，直接通过
        if request.user.is_authenticated:
            return self.get_response(request)
        
        # 未登录：根据请求类型返回不同响应
        if (request.path.startswith('/api/') or 
            request.headers.get('Accept') == 'application/json' or
            request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
            return JsonResponse({'error': '请先登录'}, status=401)
        
        # 页面请求：重定向到登录页
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())