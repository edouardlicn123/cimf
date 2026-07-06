"""
================================================================================
文件：tools.py
路径：/home/edo/cimf/core/views/tools.py
================================================================================

功能说明：
    协作工具视图，包含工具首页和工具页面

版本：
    - 1.0: 新增

依赖：
    - django.shortcuts: 渲染、跳转
    - core.node.models: Module, ToolType
"""

import inspect

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.constants import ModuleType
from core.module.models import Module
from core.module.services.module_service import ModuleService


def _get_tools_list() -> list:
    """获取所有激活的 tool 类型模块列表"""
    tool_modules = Module.objects.filter(module_type=ModuleType.TOOL, is_active=True)
    tools = []
    for mod in tool_modules:
        module_info = ModuleService.load_module_info(mod.module_id) or {}
        tools.append(
            {
                "slug": mod.module_id,
                "name": module_info.get("name", mod.module_id),
                "description": module_info.get("description", ""),
                "icon": module_info.get("icon", "bi-wrench"),
            }
        )
    return tools


@login_required
def tools_index(request):
    """协作工具首页 - 完全动态显示 tool 类型的工具模块"""
    tools = _get_tools_list()
    return render(
        request,
        "tools/tools_dashboard.html",
        {
            "tools": tools,
        },
    )


@login_required
def tools_page(request, tool_slug: str, tool_id: int | None = None):
    """协作工具页面 - 动态加载对应工具的视图"""
    tools = _get_tools_list()

    if not any(t["slug"] == tool_slug for t in tools):
        return redirect("core:tools_index")

    try:
        tool_views = __import__(f"modules.{tool_slug}.views", fromlist=[""])
        if hasattr(tool_views, "tool_view"):
            sig = inspect.signature(tool_views.tool_view)
            if len(sig.parameters) == 1:
                return tool_views.tool_view(request)
            return tool_views.tool_view(request, tool_id)
        elif hasattr(tool_views, "detail_view") and tool_id:
            return tool_views.detail_view(request, tool_id)
        elif hasattr(tool_views, "list_view"):
            return tool_views.list_view(request)
    except ImportError:
        pass

    return redirect("core:tools_index")
