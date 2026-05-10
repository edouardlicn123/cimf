# -*- coding: utf-8 -*-
"""
================================================================================
文件：jinja2.py
路径：/home/edo/cimf-v2/cimf_django/jinja2.py
================================================================================

功能说明：
    Django Jinja2 自定义配置，添加 Django 特有的模板函数和过滤器

版本：
    - 1.0: 初始版本
    - 1.1: 添加 date 过滤器
    - 1.2: 修复 url() 函数支持位置参数
"""

from django.templatetags.static import static
from django.urls import reverse
from django.utils.dateformat import format as date_format
from jinja2 import Environment


def jinja2_date_filter(value, format_string='Y-m-d H:i'):
    """Date filter for Jinja2 templates"""
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    try:
        return date_format(value, format_string)
    except Exception:
        return str(value)


def url_with_args(viewname, *args, **kwargs):
    """
    包装 reverse 函数，支持位置参数和关键字参数
    用法：{{ url('core:user_edit', user.id) }}
          {{ url('core:user_edit', user_id=user.id) }}
          {{ url('module:list') }}
    """
    # 处理关键字参数
    if args and kwargs:
        # 混合使用位置和关键字参数不支持
        return reverse(viewname, args=args, kwargs=kwargs)
    elif args:
        return reverse(viewname, args=args)
    elif kwargs:
        return reverse(viewname, kwargs=kwargs)
    else:
        return reverse(viewname)


def jinja2_truncatechars(value, length=50):
    """Truncate characters filter for Jinja2 templates"""
    if value is None:
        return ''
    if isinstance(value, int):
        value = str(value)
    if len(value) <= length:
        return value
    return value[:length] + '...'


def jinja2_slice(value, start=0, end=None):
    """Slice filter for Jinja2 templates - supports ':50' style"""
    if value is None:
        return ''
    if isinstance(value, int):
        value = str(value)
    if isinstance(value, str):
        if isinstance(start, str) and start.startswith(':'):
            end = int(start[1:])
            start = 0
        elif isinstance(start, str):
            start = int(start)
        if end is None:
            return value[start:]
        return value[start:end]
    return value


def environment(**options):
    """创建自定义 Jinja2 环境"""
    env = Environment(**options)
    
    def media(path):
        """生成媒体文件 URL"""
        from django.conf import settings
        return f"{settings.MEDIA_URL}{path}"
    
    def csrf_token():
        request = get_request()
        if request is None:
            return ''
        from django.middleware.csrf import get_token
        from django.utils.safestring import mark_safe
        token = get_token(request)
        return mark_safe(f'<input type="hidden" name="csrfmiddlewaretoken" value="{token}">')
    
    def get_request():
        """获取当前请求对象"""
        try:
            if hasattr(env, '_context_stack') and env._context_stack:
                for ctx in reversed(env._context_stack):
                    if hasattr(ctx, 'request'):
                        return ctx.request
        except Exception:
            pass
        return None
    
    # 添加 static 函数
    env.globals.update({
        'static': static,
        'url': url_with_args,
        'range': range,
        'media': media,
        'csrf_token': csrf_token,
    })
    
    # 添加过滤器
    env.filters['date'] = jinja2_date_filter
    env.filters['truncatechars'] = jinja2_truncatechars
    env.filters['slice'] = jinja2_slice
    
    return env
