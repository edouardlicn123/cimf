"""
Node 节点系统视图
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import URLPattern, URLResolver
from django.views.decorators.http import require_POST

from core.constants import ModuleType
from core.decorators import admin_required
from core.fields import get_all_field_types_info
from core.module.models import Module
from core.node.models import Node, NodeType
from core.node.services import NodeService, NodeTypeService

logger = logging.getLogger(__name__)


@login_required
def nodes_index(request):
    """节点首页 - 只显示 node 类型的节点类型"""
    node_type_ids = Module.objects.filter(
        module_type=ModuleType.NODE,
        is_active=True
    ).values_list('module_id', flat=True)
    node_types = NodeType.objects.filter(slug__in=node_type_ids, is_active=True)
    return render(request, 'node/node_dashboard.html', {
        'node_types': node_types,
        'active_section': 'dashboard',
    })


@login_required
def node_types(request):  # noqa: ARG001
    """节点类型列表（重定向到 node_types_list）"""
    return redirect('core:node_types_list')


@admin_required
def node_types_list(request):
    """可用节点类型列表页"""
    node_types = NodeTypeService.get_all_including_inactive()
    return render(request, 'node/node_types_list.html', {
        'node_types': node_types,
        'active_section': 'node_types',
    })


@admin_required
@require_POST
def node_type_delete(request, node_type_id: int):
    """删除节点类型"""
    NodeTypeService.delete(node_type_id)
    messages.success(request, '节点类型已删除')
    return redirect('core:node_types_list')


@admin_required
@require_POST
def node_type_toggle(request, node_type_id: int):
    """切换节点类型启用/禁用状态"""
    success = NodeTypeService.toggle_active(node_type_id)
    status = '启用' if success else '禁用'
    messages.success(request, f'节点类型已{status}')
    return redirect('core:node_types_list')


@login_required
def node_list(request, node_type_slug: str):
    """节点列表页"""
    node_type = get_object_or_404(NodeType, slug=node_type_slug)
    if not node_type.is_active:
        messages.error(request, '该节点类型未启用')
        return redirect('node:index')

    nodes = NodeService.get_nodes(node_type_slug)
    return render(request, 'node/node_list.html', {
        'node_type': node_type,
        'nodes': nodes,
    })


@login_required
def node_create(request, node_type_slug: str):
    """创建节点"""
    if not request.user.is_admin:
        messages.error(request, '需要管理员权限')
        return redirect('core:dashboard')

    node_type = get_object_or_404(NodeType, slug=node_type_slug)
    if not node_type.is_active:
        messages.error(request, '该节点类型未启用')
        return redirect('node:index')

    return render(request, 'node/node_edit.html', {
        'node_type': node_type,
        'node': None,
    })


@login_required
def node_view(request, node_type_slug: str, node_id: int):
    """查看节点"""
    node = get_object_or_404(Node, id=node_id, node_type__slug=node_type_slug)
    return render(request, 'node/node_detail.html', {
        'node': node,
    })


@login_required
def node_edit(request, node_type_slug: str, node_id: int):
    """编辑节点"""
    if not request.user.is_admin:
        messages.error(request, '需要管理员权限')
        return redirect('core:dashboard')

    node = get_object_or_404(Node.objects.select_related('node_type'), id=node_id, node_type__slug=node_type_slug)
    return render(request, 'node/node_edit.html', {
        'node_type': node.node_type,
        'node': node,
    })


@login_required
@require_POST
def node_delete(request, node_type_slug: str, node_id: int):
    """删除节点"""
    if not request.user.is_admin:
        messages.error(request, '需要管理员权限')
        return redirect('core:dashboard')

    node = get_object_or_404(Node, id=node_id, node_type__slug=node_type_slug)
    try:
        node.delete()
        messages.success(request, '节点已删除')
    except Exception as e:
        messages.error(request, f'删除节点失败: {e!s}')
        logger.error(f"删除节点失败: node_id={node_id}, error={e}", exc_info=True)
    return redirect('node:module_page', node_type_slug)


@admin_required
def field_types(request):
    """字段类型列表"""
    field_types_info = get_all_field_types_info()
    return render(request, 'structure/field_types/field_types.html', {
        'field_types': field_types_info,
        'active_section': 'field_types',
    })


@login_required
def field_types_api(request):  # noqa: ARG001
    """字段类型 API"""
    field_types_info = get_all_field_types_info()
    return JsonResponse({'field_types': field_types_info})


@login_required
def taxonomy_items_api(request):
    """获取词汇表项 API"""
    from core.models import Taxonomy  # noqa: PLC0415
    taxonomy_slug = request.GET.get('taxonomy')
    if not taxonomy_slug:
        return JsonResponse({'error': '缺少 taxonomy 参数'}, status=400)

    taxonomy = Taxonomy.objects.filter(slug=taxonomy_slug).first()
    if not taxonomy:
        return JsonResponse({'error': '词汇表不存在'}, status=404)

    items = taxonomy.items.values('id', 'name')
    return JsonResponse({'items': list(items)})


@login_required
def module_custom_dispatch(request, node_type_slug: str, extra_path: str):
    """处理 node 模块自定义 URL（如 nodes/customer/api/stats/）"""
    from core.module.models import Module  # noqa: PLC0415
    if not Module.objects.filter(module_id=node_type_slug, is_installed=True, is_active=True).exists():
        raise Http404
    try:
        module = __import__(f'modules.{node_type_slug}.urls', fromlist=['urlpatterns'])
        path_to_match = extra_path.strip('/')
        for pattern in module.urlpatterns:
            if isinstance(pattern, (URLResolver, URLPattern)):
                match = pattern.resolve(path_to_match)
                if match:
                    return match.func(request, **match.kwargs)
    except ImportError:
        pass
    raise Http404


@login_required
def module_dispatch(request, node_type_slug: str, node_id: int | None = None, action: str | None = None):
    """模块分发视图 - 根据节点类型动态加载对应模块的视图"""
    from core.module.models import Module  # noqa: PLC0415
    if not Module.objects.filter(module_id=node_type_slug, is_installed=True, is_active=True).exists():
        raise Http404
    module_path = node_type_slug

    try:
        module_views = __import__(f'modules.{module_path}.views', fromlist=[''])

        if action == 'create':
            if hasattr(module_views, 'node_create'):
                return module_views.node_create(request)
            elif hasattr(module_views, 'create'):
                return module_views.create(request)

        if action == 'delete':
            if hasattr(module_views, 'node_delete'):
                return module_views.node_delete(request, node_id)
            elif hasattr(module_views, 'delete'):
                return module_views.delete(request, node_id)

        if hasattr(module_views, 'module_view'):
            return module_views.module_view(request, node_id)
        elif hasattr(module_views, 'detail_view') and node_id:
            return module_views.detail_view(request, node_id)
        elif hasattr(module_views, 'list_view'):
            return module_views.list_view(request)
        elif hasattr(module_views, 'node_list') and not node_id:
            return module_views.node_list(request)
        elif hasattr(module_views, 'node_view') and node_id:
            return module_views.node_view(request, node_id)
        elif hasattr(module_views, 'node_edit') and node_id:
            return module_views.node_edit(request, node_id)
    except ImportError:
        pass

    raise Http404(f'未找到模块: {node_type_slug}')
