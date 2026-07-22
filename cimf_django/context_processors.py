"""
================================================================================
文件：context_processors.py
路径：/home/edo/cimf-v2/cimf_django/context_processors.py
================================================================================

功能说明：
    Django 模板上下文处理器，为所有模板提供公共变量

版本：
    - 1.0: 初始版本
"""

import logging
import time

from django.middleware.csrf import get_token

from core.constants import URL_SECTION_MAPPING
from core.services import PermissionService, SettingsService

logger = logging.getLogger(__name__)


def system_settings(_request):
    """
    为所有模板提供系统设置
    """
    try:
        settings = SettingsService.get_all_settings()
        return {
            "system_name": settings.get("system_name", "CIMF"),
            "system_settings": settings,
            "timestamp": int(time.time()),
        }
    except Exception:
        logger.exception("加载系统设置失败")
        return {
            "system_name": "CIMF",
            "system_settings": {},
            "timestamp": int(time.time()),
        }


def user_permissions(request):
    """
    为所有模板提供用户权限信息
    """
    if not hasattr(request, "user") or not request.user.is_authenticated:
        return {"user_permissions": []}

    try:
        permissions = PermissionService.get_user_effective_permissions(request.user)
    except Exception:
        logger.exception("获取用户权限失败")
        permissions = []
    return {"user_permissions": permissions}


def csrf_token(request):
    """
    为 Jinja2 模板提供 CSRF token 值（仅返回 token，不包含 HTML）
    HTML 渲染由 jinja2.py 中的函数处理
    """
    return {"csrf_token_value": get_token(request)}


def active_section(request):
    """从URL名称自动推断 active_section"""
    url_name = request.resolver_match.url_name if request.resolver_match else ""
    section = URL_SECTION_MAPPING.get(url_name)
    return {"active_section": section}
