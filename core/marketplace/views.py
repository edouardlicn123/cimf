# -*- coding: utf-8 -*-
"""
模块市场视图
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import admin_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .services import MarketService


@login_required
def market_index(request):
    """市场首页"""
    modules = MarketService.get_modules()
    
    # 获取筛选参数
    type_filter = request.GET.get('type', '')  # node/system/tool
    
    for module in modules:
        module_id = module.get('id', '')
        status = MarketService.get_module_status(module_id)
        module['installed'] = status['installed']
        module['installed_version'] = status['installed_version']
        module['market_version'] = status['market_version']
        module['has_update'] = status['has_update']
        # 确保有 icon 和 description 字段（用于卡片显示）
        if 'icon' not in module:
            module['icon'] = 'bi-box-seam'
        if 'description' not in module:
            module['description'] = ''
        if 'type' not in module:
            module['type'] = 'node'
    
    # 应用类型筛选
    filtered = modules
    if type_filter:
        filtered = [m for m in filtered if m.get('type', '') == type_filter]
    
    # 分页
    from django.core.paginator import Paginator
    paginator = Paginator(filtered, 12)  # 每页12个
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)
    
    # 计算页码范围
    current = page_obj.number
    start = max(1, current - 2)
    end = min(paginator.num_pages, current + 2)
    page_range = list(range(start, end + 1))
    
    # 构建基础查询字符串
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    base_query = query_params.urlencode()
    if base_query:
        base_query = '?' + base_query + '&'
    else:
        base_query = '?'
    
    return render(request, 'marketplace/index.html', {
        'modules': page_obj.object_list,
        'page_obj': page_obj,
        'page_range': page_range,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_prev': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'prev_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'type_filter': type_filter,
        'base_query': base_query,
        'active_section': 'market',
    })


@admin_required
@require_POST
def market_install(request, module_id: str):
    """下载安装模块"""

    result = MarketService.download_and_extract(module_id)
    if not result.get('success'):
        return JsonResponse(result)

    try:
        from core.module.services import ModuleService

        module = ModuleService.register_module({
            'id': module_id,
            'path': module_id,
        })
        if module:
            result['message'] = '下载成功，请在模块管理页面完成安装和启用'
            result['registered'] = True
    except Exception as e:
        result['success'] = False
        result['error'] = f'注册失败: {str(e)}'

    return JsonResponse(result)
