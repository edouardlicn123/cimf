"""模块市场视图"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.decorators import admin_post_view
from core.utils.pagination import paginate_queryset
from core.utils.response import json_success

from .services import MarketService


@login_required
def market_index(request):
    """市场首页"""
    modules = MarketService.get_modules()

    # 获取筛选参数
    type_filter = request.GET.get("type", "")  # node/system/tool

    for module in modules:
        module_id = module.get("id", "")
        status = MarketService.get_module_status(module_id)
        module["installed"] = status["installed"]
        module["installed_version"] = status["installed_version"]
        module["market_version"] = status["market_version"]
        module["has_update"] = status["has_update"]
        # 确保有 icon 和 description 字段（用于卡片显示）
        if "icon" not in module:
            module["icon"] = "bi-box-seam"
        if "description" not in module:
            module["description"] = ""
        if "type" not in module:
            module["type"] = "node"

    # 应用类型筛选
    filtered = modules
    if type_filter:
        filtered = [m for m in filtered if m.get("type", "") == type_filter]

    # 分页
    page_obj, page_range = paginate_queryset(request, filtered, per_page=12)

    # 构建基础查询字符串
    query_params = request.GET.copy()
    if "page" in query_params:
        del query_params["page"]
    base_query = query_params.urlencode()
    base_query = "?" + base_query + "&" if base_query else "?"

    return render(
        request,
        "marketplace/index.html",
        {
            "modules": page_obj.object_list,
            "page_obj": page_obj,
            "page_range": page_range,
            "type_filter": type_filter,
            "base_query": base_query,
            "active_section": "market",
        },
    )


@admin_post_view
def market_install(request, module_id: str):  # noqa: ARG001
    """下载安装模块"""
    result = MarketService.download_and_extract(module_id)
    if not result.get("success"):
        return json_success(extra=result)

    try:
        from core.module.services import ModuleService  # noqa: PLC0415

        module = ModuleService.register_module(
            {
                "id": module_id,
                "path": module_id,
            },
        )
        if module:
            result["message"] = "下载成功，请在模块管理页面完成安装和启用"
            result["registered"] = True
    except Exception as e:
        result["success"] = False
        result["error"] = f"注册失败: {e!s}"

    return json_success(extra=result)
