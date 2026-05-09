# -*- coding: utf-8 -*-
"""
地区 API 模块
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from core.services import ChinaRegionService


@login_required
@require_GET
def api_regions_provinces(request):
    """获取所有省份"""
    provinces = ChinaRegionService.get_provinces()
    return JsonResponse({
        'success': True,
        'data': [{'code': p.code, 'name': p.name} for p in provinces]
    })


@login_required
@require_GET
def api_regions_cities(request):
    """获取某省份的城市"""
    province_code = request.GET.get('province')
    if not province_code:
        return JsonResponse({'success': False, 'error': '缺少province参数'}, status=400)
    
    cities = ChinaRegionService.get_cities(province_code)
    return JsonResponse({
        'success': True,
        'data': [{'code': c.code, 'name': c.name} for c in cities]
    })


@login_required
@require_GET
def api_regions_districts(request):
    """获取某城市的区县"""
    city_code = request.GET.get('city')
    if not city_code:
        return JsonResponse({'success': False, 'error': '缺少city参数'}, status=400)
    
    districts = ChinaRegionService.get_districts(city_code)
    return JsonResponse({
        'success': True,
        'data': [{'code': d.code, 'name': d.name} for d in districts]
    })


@login_required
@require_GET
def api_regions_search(request):
    """搜索行政区划"""
    keyword = request.GET.get('q', '')
    if not keyword:
        return JsonResponse({'success': False, 'error': '缺少q参数'}, status=400)
    
    results = ChinaRegionService.search(keyword)
    return JsonResponse({
        'success': True,
        'data': [
            {
                'code': r.code,
                'name': r.name,
                'level': r.level,
                'full_path': r.full_path
            }
            for r in results
        ]
    })


@login_required
@require_GET
def api_regions_path(request):
    """获取完整路径"""
    code = request.GET.get('code')
    if not code:
        return JsonResponse({'success': False, 'error': '缺少code参数'}, status=400)
    
    path = ChinaRegionService.get_full_path(code)
    return JsonResponse({
        'success': True,
        'data': {'code': code, 'path': path}
    })


@login_required
@require_GET
def api_regions_stats(request):
    """获取统计信息"""
    stats = ChinaRegionService.get_stats()
    return JsonResponse({
        'success': True,
        'data': stats
    })