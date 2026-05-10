# -*- coding: utf-8 -*-
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

import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.module.models import Module
from core.constants import ModuleType


def _load_module_info(module_id: str) -> dict:
    """动态加载模块的 MODULE_INFO"""
    try:
        import importlib.util
        module_path = os.path.join('modules', module_id, 'module.py')
        spec = importlib.util.spec_from_file_location(f'modules.{module_id}.module', module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, 'MODULE_INFO', {})
    except Exception:
        pass
    return {}


@login_required
def tools_index(request):
    """协作工具首页 - 完全动态显示 tool 类型的工具模块"""
    tool_modules = Module.objects.filter(
        module_type=ModuleType.TOOL,
        is_active=True
    )
    tools = []
    for mod in tool_modules:
        module_info = _load_module_info(mod.module_id)
        tools.append({
            'slug': mod.module_id,
            'name': module_info.get('name', mod.module_id),
            'description': module_info.get('description', ''),
            'icon': module_info.get('icon', 'bi-wrench'),
        })
    return render(request, 'tools/tools_dashboard.html', {
        'tools': tools,
        'active_section': 'dashboard',
    })


@login_required
def tools_page(request, tool_slug: str, tool_id: int = None):
    """协作工具页面 - 动态加载对应工具的视图"""
    tool_modules = Module.objects.filter(
        module_type=ModuleType.TOOL,
        is_active=True
    )
    tools = []
    for mod in tool_modules:
        module_info = _load_module_info(mod.module_id)
        tools.append({
            'slug': mod.module_id,
            'name': module_info.get('name', mod.module_id),
            'description': module_info.get('description', ''),
            'icon': module_info.get('icon', 'bi-wrench'),
        })
    
    try:
        tool_views = __import__(f'modules.{tool_slug}.views', fromlist=[''])
        if hasattr(tool_views, 'tool_view'):
            import inspect
            sig = inspect.signature(tool_views.tool_view)
            if len(sig.parameters) == 1:
                return tool_views.tool_view(request)
            return tool_views.tool_view(request, tool_id)
        elif hasattr(tool_views, 'detail_view') and tool_id:
            return tool_views.detail_view(request, tool_id)
        elif hasattr(tool_views, 'list_view'):
            return tool_views.list_view(request)
    except ImportError:
        pass
    
    return redirect('core:tools_index')