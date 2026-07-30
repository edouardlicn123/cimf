"""
Node 模块基础视图工厂

为 node 类型模块提供标准 CRUD 视图工厂函数。
使用 partial application 方式消除重复的视图模式。

用法：
    from core.node.base_node_view import make_api_stats_view, make_node_view, make_node_delete

    api_stats = make_api_stats_view(MyService)
    node_view = make_node_view(MyService, module_slug='my_module', obj_context_key='my_obj')
    node_delete = make_node_delete(MyService, module_slug='my_module')
"""

import logging

from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render

from core.decorators import login_required, login_required_json
from core.node.services import NodeService, NodeTypeService
from core.services.permission_service import PermissionService

logger = logging.getLogger(__name__)


def make_api_stats_view(service_class):
    """创建节点模块的标准 API 统计视图

    返回一个 JSON 响应，包含 total 和 recent 计数值。
    由各模块 views.py 调用后赋值给 api_stats 变量。
    """
    @login_required_json
    def api_stats(request):  # noqa: ARG001
        total = service_class.get_count()
        recent = service_class.get_recent_count(days=7)
        return JsonResponse({
            "success": True,
            "data": {
                "total": total,
                "recent": recent,
            },
        })
    return api_stats


def make_node_view(service_class, *, module_slug, obj_context_key,
                   label_name, template_name=None, extra_context_fn=None):
    """创建节点模块的详情查看视图

    参数：
        service_class: 模块服务类（必须有 get_by_node_id 方法）
        module_slug:   模块 slug（用于重定向 URL）
        obj_context_key: 模板中数据对象的变量名
        label_name:    中文名称，用于提示信息（如 '居民'、'客户'）
        template_name: 模板路径，默认 f'{module_slug}/view.html'
        extra_context_fn: 额外的模板上下文函数，签名 (obj, node, request) -> dict
    """
    if template_name is None:
        template_name = f'{module_slug}/view.html'

    @login_required
    def node_view(request, node_id: int):
        node = NodeService.get_by_id(node_id)
        if not node:
            raise Http404('节点不存在')

        has_perm, error_msg = PermissionService.check_node_permission(request.user, node, 'view')
        if not has_perm:
            messages.error(request, error_msg)
            return redirect('node:module_page', module_slug)

        obj = service_class.get_by_node_id(node_id)
        if not obj:
            messages.error(request, f'{label_name}信息不存在')
            return redirect('node:module_page', module_slug)

        context = {
            'node_type': node.node_type,
            'node_types': NodeTypeService.get_all(),
            'node': node,
            obj_context_key: obj,
            'active_section': module_slug,
        }
        if extra_context_fn:
            context.update(extra_context_fn(obj, node, request))
        return render(request, template_name, context)

    return node_view


def make_node_delete(service_class, *, module_slug, label_name=None, delete_method='delete'):
    """创建节点模块的删除视图

    参数：
        service_class: 模块服务类（必须有 get_by_node_id 方法）
        module_slug:   模块 slug（用于重定向 URL）
        label_name:    中文名称，默认取 module_slug
        delete_method: 删除方法名，默认 'delete'；签名 (obj_id) -> bool
    """
    if label_name is None:
        label_name = module_slug

    @login_required
    def node_delete(request, node_id: int):
        if request.method != 'POST':
            return redirect('node:module_page', module_slug)

        node = NodeService.get_by_id(node_id)
        if not node:
            messages.error(request, f'{label_name}信息不存在')
            return redirect('node:module_page', module_slug)

        has_perm, error_msg = PermissionService.check_node_permission(request.user, node, 'delete')
        if not has_perm:
            messages.error(request, error_msg)
            return redirect('node:module_page', module_slug)

        obj = service_class.get_by_node_id(node_id)
        if not obj:
            messages.error(request, f'{label_name}信息不存在')
            return redirect('node:module_page', module_slug)

        getattr(service_class, delete_method)(obj.id)
        messages.success(request, f'{label_name}已删除')
        return redirect('node:module_page', module_slug)

    return node_delete
