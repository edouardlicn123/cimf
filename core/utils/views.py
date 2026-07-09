from importlib import import_module

from django.contrib import messages
from django.shortcuts import redirect


def dynamic_import_view(module_path: str, view_name: str, views_module: str = "views"):
    """Dynamically import a view function from a module"""
    try:
        module = import_module(f"modules.{module_path}.{views_module}")
        return getattr(module, view_name, None)
    except (ImportError, AttributeError):
        return None


def safe_int(value: str, default=None):
    """安全地将字符串转换为整数"""
    if not value:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def redirect_with_error(request, message, url_name, *args, **kwargs):
    messages.error(request, message)
    return redirect(url_name, *args, **kwargs)


def redirect_with_success(request, message, url_name, *args, **kwargs):
    messages.success(request, message)
    return redirect(url_name, *args, **kwargs)
