"""
===============================================================================
文件：views.py
路径：/home/edo/cimf-v2/modules/customer/views.py
===============================================================================

功能说明：
    海外客户模块视图

版本：
    - 1.0: 从 modules/views.py 拆分

依赖：
    - django: Web 框架
    - modules.customer.services: 海外客户服务
    - core.node.services: Node服务
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from core.decorators import login_required_json
from core.node.services import NodeService, NodeTypeService
from core.services import PermissionService, TaxonomyService
from core.utils.pagination import paginate_queryset
from modules.customer.forms import CustomerForm
from modules.customer.services import CustomerService


def safe_int(value: str, default=None):
    """安全地将字符串转换为整数"""
    if not value:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def _get_node_or_404(node_id):
    node = NodeService.get_by_id(node_id)
    if not node:
        raise Http404("节点不存在")
    return node


def _get_customer_context(node_type, customer=None, node=None):
    form_data = _load_customer_form_data()
    return {
        "node_type": node_type,
        "node_types": NodeTypeService.get_all(),
        "node": node,
        "customer": customer,
        "active_section": "customer",
        "customer_types": form_data["customer_type"],
        "customer_levels": form_data["customer_level"],
        "enterprise_types": form_data["economic_type"],
        "countries": [{"id": c.id, "name": c.name} for c in form_data["country"]],
    }


def check_customer_permission(user, node, permission_type: str):
    """检查客户节点操作权限"""
    if user.is_admin:
        return True, None

    is_creator = node.created_by_id == user.id

    if is_creator:
        return True, None

    perm_map = {
        "view": "node.customer.view_others",
        "edit": "node.customer.edit_others",
        "delete": "node.customer.delete_others",
    }

    perm = perm_map.get(permission_type)
    if perm and PermissionService.has_permission(user, perm):
        return True, None

    return False, f"您没有权限{permission_type}别人的客户信息"


def _load_customer_form_data():
    """加载客户表单所需的分类数据"""
    slugs = ["customer_type", "customer_level", "economic_type", "country"]
    result = {}
    for slug in slugs:
        tax = TaxonomyService.get_taxonomy_by_slug(slug)
        result[slug] = TaxonomyService.get_items(tax.id) if tax else []
    return result


def _build_customer_data(cd: dict) -> dict:
    """从 cleaned_data 构建服务层数据字典"""
    return {
        "customer_name": cd.get("customer_name", "").strip(),
        "customer_code": cd.get("customer_code", "").strip() or None,
        "customer_type_id": cd.get("customer_type").id if cd.get("customer_type") else None,
        "enterprise_name": cd.get("enterprise_name", "").strip() or None,
        "phone1": cd.get("phone1", "").strip() or None,
        "email1": cd.get("email1", "").strip() or None,
        "phone2": cd.get("phone2", "").strip() or None,
        "email2": cd.get("email2", "").strip() or None,
        "linkedin": cd.get("linkedin", "").strip() or None,
        "country_id": cd.get("country").id if cd.get("country") else None,
        "province": cd.get("province", "").strip() or None,
        "address": cd.get("address", "").strip() or None,
        "postal_code": cd.get("postal_code", "").strip() or None,
        "industry": cd.get("industry", "").strip() or None,
        "enterprise_type_id": cd.get("enterprise_type").id if cd.get("enterprise_type") else None,
        "registered_capital": cd.get("registered_capital"),
        "customer_level_id": cd.get("customer_level").id if cd.get("customer_level") else None,
        "credit_limit": cd.get("credit_limit"),
        "website": cd.get("website", "").strip() or None,
        "notes": cd.get("notes", "").strip() or None,
    }


def _process_customer_form(request, customer=None, node=None):
    form = CustomerForm(request.POST)
    if form.is_valid():
        data = _build_customer_data(form.cleaned_data)
        try:
            if customer:
                CustomerService.update(customer.id, request.user, data)
                messages.success(request, "客户更新成功")
                return redirect("node:node_view", node_type_slug="customer", node_id=node.id)
            CustomerService.create(request.user, data)
            messages.success(request, "客户创建成功")
            return redirect("node:module_page", node_type_slug="customer")
        except ValueError as e:
            messages.error(request, str(e))
    else:
        for field, errors in form.errors.items():
            label = form.fields[field].label or field
            for error in errors:
                messages.error(request, f"{label}: {error}")
    return None


@login_required
def node_list(request):
    """海外客户列表"""
    node_type = NodeTypeService.get_by_slug("customer")
    if not node_type:
        raise Http404("节点类型不存在")

    search = request.GET.get("search", "")
    customer_type_filter = request.GET.get("customer_type", "")
    customer_level_filter = request.GET.get("customer_level", "")
    node_types = NodeTypeService.get_all()

    form_data = _load_customer_form_data()
    customer_types = [{"id": c.id, "name": c.name} for c in form_data["customer_type"]]
    customer_levels = [{"id": c.id, "name": c.name} for c in form_data["customer_level"]]

    customer_type_id = safe_int(customer_type_filter)
    customer_level_id = safe_int(customer_level_filter)

    customers = CustomerService.get_list(
        search if search else None,
        customer_type_id=customer_type_id,
        customer_level_id=customer_level_id,
        user=request.user,
    )

    page_obj, _ = paginate_queryset(request, customers, per_page=10)

    return render(
        request,
        "list.html",
        {
            "node_type": node_type,
            "node_types": node_types,
            "customers": page_obj.object_list,
            "search": search,
            "active_section": "customer",
            "filter_customer_type": customer_type_filter,
            "filter_customer_level": customer_level_filter,
            "customer_types": customer_types,
            "customer_levels": customer_levels,
            "page_obj": page_obj,
        },
    )


@login_required
def node_create(request):
    """创建海外客户"""
    node_type = NodeTypeService.get_by_slug("customer")
    if not node_type:
        raise Http404("节点类型不存在")

    if request.method == "POST":
        response = _process_customer_form(request)
        if response:
            return response

    return render(request, "edit.html", _get_customer_context(node_type))


@login_required
def node_view(request, node_id: int):
    """查看海外客户"""
    node = _get_node_or_404(node_id)

    has_perm, error_msg = check_customer_permission(request.user, node, "view")
    if not has_perm:
        messages.error(request, error_msg)
        return redirect("node:module_page", node_type_slug="customer")

    node_types = NodeTypeService.get_all()

    customer = CustomerService.get_by_node_id(node_id)
    if not customer:
        messages.error(request, "客户不存在")
        return redirect("node:module_page", node_type_slug="customer")

    return render(
        request,
        "view.html",
        {
            "node_type": node.node_type,
            "node_types": node_types,
            "node": node,
            "customer": customer,
            "active_section": "customer",
        },
    )


@login_required
def node_edit(request, node_id: int):
    """编辑海外客户"""
    node = _get_node_or_404(node_id)

    has_perm, error_msg = check_customer_permission(request.user, node, "edit")
    if not has_perm:
        messages.error(request, error_msg)
        return redirect("node:node_view", node_type_slug="customer", node_id=node_id)

    customer = CustomerService.get_by_node_id(node_id)
    if not customer:
        messages.error(request, "客户不存在")
        return redirect("node:module_page", node_type_slug="customer")

    if request.method == "POST":
        response = _process_customer_form(request, customer, node)
        if response:
            return response

    return render(request, "edit.html", _get_customer_context(node.node_type, customer, node))


@login_required
@require_POST
def node_delete(request, node_id: int):
    """删除海外客户"""
    node = NodeService.get_by_id(node_id)
    if node:
        has_perm, error_msg = check_customer_permission(request.user, node, "delete")
        if not has_perm:
            messages.error(request, error_msg)
        else:
            customer = CustomerService.get_by_node_id(node_id)
            if customer:
                CustomerService.delete(customer.id)
                messages.success(request, "客户已删除")
            else:
                messages.error(request, "客户不存在")

    return redirect("node:module_page", node_type_slug="customer")


@login_required_json
def api_stats(request):  # noqa: ARG001
    """获取客户统计信息"""
    total = CustomerService.get_count()
    recent = CustomerService.get_recent_count(days=7)

    return JsonResponse(
        {
            "success": True,
            "data": {
                "total": total,
                "recent": recent,
            },
        }
    )
