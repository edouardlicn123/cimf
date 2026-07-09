"""IP 访问限制中间件

提供两层安全控制：
1. IPWhitelistMiddleware — 按客户端 IP 限制访问来源
2. GlobalLoginRequiredMiddleware — 全局登录要求

---
IPWhitelistMiddleware 白名单来源优先级：
  第一来源：DJANGO_IP_WHITELIST（显式配置，支持 CIDR）
  第二来源：DJANGO_ALLOWED_HOSTS（自动提取其中的 IP 地址）

这样用户只需维护 DJANGO_ALLOWED_HOSTS 一处即可同时控制 Host 头校验和 IP 白名单。
DJANGO_IP_WHITELIST 作为可选扩展，用于需要 CIDR 段等高级场景。

对比：
  ALLOWED_HOSTS        → 校验 HTTP Host 头（防 Host 头攻击）
  IPWhitelistMiddleware → 校验客户端真实 IP（防非授权访问）
  两者互补，缺一不可。
"""

import ipaddress
import logging

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponse

from core.utils.response import json_error

logger = logging.getLogger(__name__)


class IPWhitelistMiddleware:
    """按客户端 IP 限制访问的中间件

    启用后，所有请求来源 IP 必须在白名单内，否则返回 403。
    白名单支持以下格式：
      - 单个 IP:  192.168.1.1
      - CIDR 段:  192.168.1.0/24
    配置项见 django.conf.settings.IP_RESTRICTION_ENABLED 和 IP_WHITELIST。
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, "IP_RESTRICTION_ENABLED", False)
        self.whitelist = getattr(settings, "IP_WHITELIST", [])
        self._compiled_whitelist = []

        # 第一来源：显式配置的 IP_WHITELIST
        for ip_str in self.whitelist:
            self._add_to_whitelist(ip_str)

        # 第二来源：IP_WHITELIST 未配置时，自动从 ALLOWED_HOSTS 提取 IP 地址
        # ALLOWED_HOSTS 中可能包含域名（localhost, example.com），
        # 这些在解析 IP 时会抛出 ValueError 被静默跳过，不影响正常流程。
        if self.enabled and not self._compiled_whitelist:
            for host in settings.ALLOWED_HOSTS:
                self._add_to_whitelist(host)

    def _add_to_whitelist(self, ip_str):
        try:
            if "/" in ip_str:
                self._compiled_whitelist.append(ipaddress.ip_network(ip_str, strict=False))
            else:
                self._compiled_whitelist.append(ipaddress.ip_address(ip_str))
        except ValueError:
            logger.warning(f"无效的IP配置: {ip_str}")

    def __call__(self, request):
        if not self.enabled:
            return self.get_response(request)

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        client_ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.META.get("REMOTE_ADDR", "")

        if not self._is_ip_allowed(client_ip):
            logger.warning(
                f"IP访问被拒绝: {client_ip} - {request.method} {request.path} - "
                f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}",
            )
            if "application/json" in request.headers.get("Accept", ""):
                return json_error("拒绝访问：您的IP不在允许范围内", 403)
            return HttpResponse("<h1>403 Forbidden</h1><p>拒绝访问：您的IP不在允许范围内</p>", status=403)

        return self.get_response(request)

    def _is_ip_allowed(self, client_ip):
        try:
            client_addr = ipaddress.ip_address(client_ip)
            for item in self._compiled_whitelist:
                if isinstance(item, ipaddress.IPv4Network):
                    if client_addr in item:
                        return True
                elif client_addr == item:
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
            "/accounts/login/",
            "/admin/login/",
        ]

    def __call__(self, request):
        # 检查是否在白名单
        if any(request.path.startswith(url) for url in self.whitelist):
            return self.get_response(request)

        # 已登录，直接通过
        if request.user.is_authenticated:
            return self.get_response(request)

        # 未登录：根据请求类型返回不同响应
        if (
            request.path.startswith("/api/")
            or request.headers.get("Accept") == "application/json"
            or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        ):
            return json_error("请先登录", 401)

        # 页面请求：重定向到登录页
        return redirect_to_login(request.get_full_path())
