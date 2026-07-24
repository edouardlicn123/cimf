"""
自定义 Django 检查：自动检测认证、Admin、Signal、模板表单等常见问题
运行：./venv/bin/python manage.py check
"""

from . import (
    admin_check,
    scanner_checks,
    signal_check,
    template_check,
    views_check,
)
