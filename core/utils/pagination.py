# -*- coding: utf-8 -*-
"""
通用分页工具函数
"""

from django.core.paginator import Paginator


def paginate_queryset(request, queryset, per_page=10):
    """
    通用分页工具函数
    
    Args:
        request: Django HttpRequest 对象
        queryset: Django QuerySet 对象或列表
        per_page: 每页记录数，默认 10
    
    Returns:
        dict: 包含分页相关数据的字典，可直接传入 render() 的 context
    """
    try:
        page_num = int(request.GET.get('page', 1))
        if page_num < 1:
            page_num = 1
    except (ValueError, TypeError):
        page_num = 1
    
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_num)
    
    return {
        'page_obj': page_obj,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_prev': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'prev_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    }
