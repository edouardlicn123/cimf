"""
地区 API 模块
"""

from core.decorators import api_get_view
from core.services import ChinaRegionService
from core.utils.response import json_error, json_success


def _require_param(params, param_name, error_message=None):  # noqa: ARG001
    value = params.get(param_name)
    if not value:
        return None
    return value


@api_get_view
def api_regions_provinces(request):  # noqa: ARG001
    """获取所有省份"""
    provinces = ChinaRegionService.get_provinces()
    return json_success([{"code": p.code, "name": p.name} for p in provinces])


@api_get_view
def api_regions_cities(request):
    """获取某省份的城市"""
    province_code = _require_param(request.GET, "province")
    if province_code is None:
        return json_error("缺少province参数", 400)

    cities = ChinaRegionService.get_cities(province_code)
    return json_success([{"code": c.code, "name": c.name} for c in cities])


@api_get_view
def api_regions_districts(request):
    """获取某城市的区县"""
    city_code = _require_param(request.GET, "city")
    if city_code is None:
        return json_error("缺少city参数", 400)

    districts = ChinaRegionService.get_districts(city_code)
    return json_success([{"code": d.code, "name": d.name} for d in districts])


@api_get_view
def api_regions_search(request):
    """搜索行政区划"""
    keyword = _require_param(request.GET, "q")
    if keyword is None:
        return json_error("缺少q参数", 400)

    results = ChinaRegionService.search(keyword)
    return json_success([{"code": r.code, "name": r.name, "level": r.level, "full_path": r.full_path} for r in results])


@api_get_view
def api_regions_path(request):
    """获取完整路径"""
    code = _require_param(request.GET, "code")
    if code is None:
        return json_error("缺少code参数", 400)

    path = ChinaRegionService.get_full_path(code)
    return json_success({"code": code, "path": path})


@api_get_view
def api_regions_stats(request):  # noqa: ARG001
    """获取统计信息"""
    stats = ChinaRegionService.get_stats()
    return json_success(stats)
