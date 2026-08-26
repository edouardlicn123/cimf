import json
import logging

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from core.decorators import permission_required
from core.importexport import ExportService
from core.node.services import NodeTypeService

logger = logging.getLogger(__name__)


def _get_node_type_or_redirect(node_type_slug, redirect_name="importexport:export_list"):
    """获取 NodeType，不存在时重定向"""
    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        return None, redirect(redirect_name)
    return node_type, None


@permission_required("importexport.view")
def export_list(request):
    """导出页 - 显示所有模块的导出入口"""
    node_types = NodeTypeService.get_all()
    return render(
        request,
        "importexport/export.html",
        {
            "node_types": node_types,
            "active_section": "export",
        },
    )


@permission_required("importexport.view")
@require_http_methods(["GET", "POST"])
def export_select_fields(request, node_type_slug):
    """字段选择页"""
    node_type, response = _get_node_type_or_redirect(node_type_slug)
    if response:
        return response

    if request.method == "POST":
        selected_fields = []
        for key in request.POST:
            if key.startswith("field_"):
                value = request.POST.get(key)
                if value and value.strip():
                    selected_fields.append(value.strip())

        if not selected_fields:
            messages.error(request, "请至少选择一个导出字段")
            return redirect("importexport:export_select_fields", node_type_slug)

        request.session["export_selected_fields"] = selected_fields
        allowed_formats = {"csv", "xlsx"}
        export_format = request.POST.get("format", "csv")
        if export_format not in allowed_formats:
            export_format = "csv"
        request.session["export_format"] = export_format

        filters = []
        for i in range(6):
            f_field = request.POST.get(f"filter_field_{i}", "")
            f_value = request.POST.get(f"filter_value_{i}", "")
            if f_field and f_value:
                filters.append({"field": f_field, "value": f_value.strip()})

        region_province = request.POST.get("filter_region_province", "")
        region_city = request.POST.get("filter_region_city", "")
        region_district = request.POST.get("filter_region_district", "")
        if region_province or region_city or region_district:
            filters.append(
                {
                    "field": "region",
                    "value": json.dumps(
                        {"province": region_province, "city": region_city, "district": region_district},
                        ensure_ascii=False,
                    ),
                }
            )

        request.session["export_filters"] = filters
        return redirect("importexport:export_confirm", node_type_slug)

    fields = ExportService.get_exportable_fields(node_type_slug)
    filterable_fields = ExportService.get_filterable_fields(node_type_slug)
    has_region = ExportService.has_region_field(node_type_slug)

    return render(
        request,
        "importexport/export_fields.html",
        {
            "node_type": node_type,
            "fields": fields,
            "filterable_fields": filterable_fields,
            "has_region": has_region,
            "active_section": "export",
        },
    )


@permission_required("importexport.view")
@require_http_methods(["GET", "POST"])
def export_confirm(request, node_type_slug):
    """确认页"""
    node_type, response = _get_node_type_or_redirect(node_type_slug)
    if response:
        return response

    selected_fields = request.session.get("export_selected_fields", [])
    export_format = request.session.get("export_format", "csv")
    filters = request.session.get("export_filters", [])

    if request.method == "POST":
        return redirect("importexport:export_exporting", node_type_slug)

    if not selected_fields:
        return redirect("importexport:export_select_fields", node_type_slug)

    fields_info = ExportService.get_fields_info(node_type_slug, selected_fields)
    record_count = ExportService.get_record_count(node_type_slug, filters)
    preview_data = ExportService.get_preview(node_type_slug, selected_fields, filters, limit=5)

    filter_summaries = ExportService.build_filter_summaries(node_type_slug, filters)

    return render(
        request,
        "importexport/export_confirm.html",
        {
            "node_type": node_type,
            "selected_fields": selected_fields,
            "fields_info": fields_info,
            "export_format": export_format,
            "record_count": record_count,
            "preview_data": preview_data,
            "filter_summaries": filter_summaries,
            "active_section": "export",
        },
    )


@permission_required("importexport.view")
def export_exporting(request, node_type_slug):
    """导出中页"""
    node_type, response = _get_node_type_or_redirect(node_type_slug)
    if response:
        return response

    selected_fields = request.session.get("export_selected_fields", [])
    if not selected_fields:
        return redirect("importexport:export_select_fields", node_type_slug)

    return render(
        request,
        "importexport/export_exporting.html",
        {
            "node_type": node_type,
            "active_section": "export",
        },
    )


@permission_required("importexport.view")
@require_http_methods(["POST"])
def do_export(request, node_type_slug):
    """执行导出"""
    _node_type, response = _get_node_type_or_redirect(node_type_slug)
    if response:
        return response

    selected_fields = request.session.get("export_selected_fields", [])
    export_format = request.session.get("export_format", "csv")
    filters = request.session.get("export_filters", [])

    if not selected_fields:
        return redirect("importexport:export_select_fields", node_type_slug)

    try:
        response = ExportService.export(node_type_slug, selected_fields, export_format, filters)
        del request.session["export_selected_fields"]
        del request.session["export_format"]
        if "export_filters" in request.session:
            del request.session["export_filters"]
        return response
    except Exception as e:
        logger.exception("导出失败: node_type=%s", node_type_slug)
        messages.error(request, f"导出失败：{e!s}")
        return redirect("importexport:export_select_fields", node_type_slug)
