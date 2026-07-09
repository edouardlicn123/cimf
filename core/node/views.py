"""
Node 节点系统视图
"""

import inspect
import logging
from importlib import import_module

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import URLPattern, URLResolver

from core.constants import ModuleType
from core.decorators import admin_post_view, admin_required
from core.fields import get_all_field_types_info
from core.module.models import Module
from core.node.models import Node, NodeType
from core.models import Taxonomy
from core.node.services import NodeService, NodeTypeService
from core.utils.pagination import paginate_queryset
from core.utils.response import json_error, json_success
from core.utils.views import dynamic_import_view

logger = logging.getLogger(__name__)


@login_required
def nodes_index(request):
    """节点首页 - 只显示 node 类型的节点类型"""
    node_type_ids = Module.get_active_ids(ModuleType.NODE)
    node_types = NodeType.objects.filter(slug__in=node_type_ids, is_active=True)
    return render(
        request,
        "node/node_dashboard.html",
        {
            "node_types": node_types,
            "active_section": "dashboard",
        },
    )


@admin_required
def node_types_list(request):
    """可用节点类型列表页"""
    node_types = NodeTypeService.get_all_including_inactive()
    return render(
        request,
        "node/node_types_list.html",
        {
            "node_types": node_types,
            "active_section": "node_types",
        },
    )


@admin_post_view
def node_type_delete(request, node_type_id: int):
    """删除节点类型"""
    if NodeTypeService.delete(node_type_id):
        messages.success(request, "节点类型已删除")
    else:
        messages.error(request, "节点类型不存在")
    return redirect("core:node_types_list")


@admin_post_view
def node_type_toggle(request, node_type_id: int):
    """切换节点类型启用/禁用状态"""
    success = NodeTypeService.toggle_active(node_type_id)
    if success is None:
        messages.error(request, "节点类型不存在")
    else:
        status = "启用" if success else "禁用"
        messages.success(request, f"节点类型已{status}")
    return redirect("core:node_types_list")


@login_required
def node_list(request, node_type_slug: str):
    """节点列表页"""
    node_type = get_object_or_404(NodeType, slug=node_type_slug)
    if not node_type.is_active:
        messages.error(request, "该节点类型未启用")
        return redirect("node:index")

    nodes = NodeService.get_nodes(node_type_slug)
    page_obj, page_range = paginate_queryset(request, nodes, per_page=20)
    return render(
        request,
        "node/node_list.html",
        {
            "node_type": node_type,
            "nodes": page_obj.object_list,
            "page_obj": page_obj,
            "page_range": page_range,
        },
    )


@admin_required
def node_create(request, node_type_slug: str):
    """创建节点"""
    node_type = get_object_or_404(NodeType, slug=node_type_slug)
    if not node_type.is_active:
        messages.error(request, "该节点类型未启用")
        return redirect("node:index")

    return render(
        request,
        "node/node_edit.html",
        {
            "node_type": node_type,
            "node": None,
        },
    )


@login_required
def node_view(request, node_type_slug: str, node_id: int):
    """查看节点"""
    node = get_object_or_404(Node, id=node_id, node_type__slug=node_type_slug)
    return render(
        request,
        "node/node_detail.html",
        {
            "node": node,
        },
    )


@admin_required
def node_edit(request, node_type_slug: str, node_id: int):
    """编辑节点"""
    node = get_object_or_404(Node.objects.select_related("node_type"), id=node_id, node_type__slug=node_type_slug)
    return render(
        request,
        "node/node_edit.html",
        {
            "node_type": node.node_type,
            "node": node,
        },
    )


@admin_post_view
def node_delete(request, node_type_slug: str, node_id: int):
    """删除节点"""
    node = get_object_or_404(Node, id=node_id, node_type__slug=node_type_slug)
    try:
        node.delete()
        messages.success(request, "节点已删除")
    except Exception as e:
        messages.error(request, f"删除节点失败: {e!s}")
        logger.error(f"删除节点失败: node_id={node_id}, error={e}", exc_info=True)
    return redirect("node:module_page", node_type_slug)


@admin_required
def field_types(request):
    """字段类型列表"""
    field_types_info = get_all_field_types_info()
    return render(
        request,
        "structure/field_types/field_types.html",
        {
            "field_types": field_types_info,
            "active_section": "field_types",
        },
    )


@login_required
def field_types_api(request):  # noqa: ARG001
    """字段类型 API"""
    field_types_info = get_all_field_types_info()
    return json_success(extra={"field_types": field_types_info})


@login_required
def taxonomy_items_api(request):
    """获取词汇表项 API"""
    taxonomy_slug = request.GET.get("taxonomy")
    if not taxonomy_slug:
        return json_error("缺少 taxonomy 参数", 400)

    taxonomy = Taxonomy.objects.filter(slug=taxonomy_slug).first()
    if not taxonomy:
        return json_error("词汇表不存在", 404)

    items = taxonomy.items.values("id", "name")
    return json_success(extra={"items": list(items)})


@login_required
def module_custom_dispatch(request, node_type_slug: str, extra_path: str):
    """处理 node 模块自定义 URL（如 nodes/customer/api/stats/）"""
    from core.module.models import Module  # noqa: PLC0415

    if not Module.objects.filter(module_id=node_type_slug, is_installed=True, is_active=True).exists():
        raise Http404
    try:
        module = import_module(f"modules.{node_type_slug}.urls")
        path_to_match = extra_path.strip("/")
        for pattern in module.urlpatterns:
            if isinstance(pattern, (URLResolver, URLPattern)):
                match = pattern.resolve(path_to_match)
                if match:
                    return match.func(request, **match.kwargs)
    except ImportError:
        pass
    raise Http404


def _check_module_exists(node_type_slug: str) -> str:
    """检查模块是否存在并已激活，返回模块路径或抛出 404"""
    from core.module.models import Module  # noqa: PLC0415

    if not Module.objects.filter(module_id=node_type_slug, is_installed=True, is_active=True).exists():
        raise Http404
    module_path = node_type_slug

    try:
        import_module(f"modules.{module_path}.views")
    except ImportError:
        raise Http404(f"未找到模块: {node_type_slug}") from None
    return module_path


def _check_action_permission(request, action: str | None, node_type_slug: str):
    """检查是否需要管理员权限，无权限时返回 redirect"""
    if action in ("create", "edit", "delete") and not request.user.is_admin:
        messages.error(request, "需要管理员权限")
        return redirect("node:module_page", node_type_slug=node_type_slug)
    return None


def _resolve_view(module_path: str, action: str | None, node_id: int | None = None):
    """解析动作对应的视图函数"""
    if action == "create":
        return dynamic_import_view(module_path, "node_create") or dynamic_import_view(module_path, "create")
    if action == "delete":
        return dynamic_import_view(module_path, "node_delete") or dynamic_import_view(module_path, "delete")
    if action == "edit":
        return dynamic_import_view(module_path, "node_edit") or dynamic_import_view(module_path, "edit")

    return (dynamic_import_view(module_path, "module_view") or
            (dynamic_import_view(module_path, "detail_view") if node_id is not None else None) or
            dynamic_import_view(module_path, "list_view") or
            (dynamic_import_view(module_path, "node_list") if node_id is None else None) or
            (dynamic_import_view(module_path, "node_view") if node_id is not None else None) or
            (dynamic_import_view(module_path, "node_edit") if node_id is not None else None))


@login_required
def module_dispatch(request, node_type_slug: str, node_id: int | None = None, action: str | None = None):
    """模块分发视图 - 根据节点类型动态加载对应模块的视图"""
    module_path = _check_module_exists(node_type_slug)

    permission_response = _check_action_permission(request, action, node_type_slug)
    if permission_response:
        return permission_response

    view = _resolve_view(module_path, action, node_id)
    if view:
        sig = inspect.signature(view)
        if len(sig.parameters) == 1:
            return view(request)
        return view(request, node_id)

    raise Http404(f"未找到模块: {node_type_slug}")
