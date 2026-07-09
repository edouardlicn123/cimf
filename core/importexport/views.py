"""
导入导出视图
"""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from core.decorators import login_required_json, permission_required
from core.importexport import ExportService, ImportService, TemplateGenerator
from core.node.services import NodeTypeService
from core.utils.response import json_error, json_success





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


@login_required
@require_POST
@permission_required("importexport.view")
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
        messages.error(request, f"导出失败：{e!s}")
        return redirect("importexport:export_select_fields", node_type_slug)


@permission_required("importexport.view")
def import_list(request):
    """导入页 - 显示所有模块的导入入口"""
    node_types = NodeTypeService.get_all()
    return render(
        request,
        "importexport/import.html",
        {
            "node_types": node_types,
            "active_section": "import",
        },
    )


@permission_required("importexport.view")
def import_page(request, node_type_slug):
    """导入操作页"""
    node_type, response = _get_node_type_or_redirect(node_type_slug, "importexport:import_list")
    if response:
        return response

    fields = ImportService.get_importable_fields(node_type_slug)

    return render(
        request,
        "importexport/import_page.html",
        {
            "node_type": node_type,
            "fields": fields,
            "active_section": "import",
        },
    )


@permission_required("importexport.view")
def download_template(request, node_type_slug):  # noqa: ARG001
    """下载导入模板"""
    _node_type, response = _get_node_type_or_redirect(node_type_slug, "importexport:import_list")
    if response:
        return response

    return TemplateGenerator.generate(node_type_slug)


@login_required_json
@require_POST
@permission_required("importexport.view")
def upload_preview(request, node_type_slug):
    """上传并预览数据 - AJAX"""
    _node_type, response = _get_node_type_or_redirect(node_type_slug, "importexport:import_list")
    if response:
        return response

    file = request.FILES.get("file")
    if not file:
        return json_error("请选择文件", 400)

    filename = file.name

    # 验证文件大小（最大 10MB）
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        return json_error("文件大小不能超过 10MB", 400)

    # 验证文件扩展名
    allowed_extensions = [".csv", ".xlsx", ".xls"]
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        return json_error("只允许上传 CSV 或 Excel 文件", 400)

    format = "xlsx" if filename.lower().endswith((".xlsx", ".xls")) else "csv"

    try:
        headers, data_rows = ImportService.read_file(file, format)

        if not headers:
            return json_error("文件为空或格式不正确", 400)

        fields = ImportService.get_importable_fields(node_type_slug)
        header_to_field = ImportService.map_headers_to_fields(headers, fields)
        parsed_rows = ImportService.parse_data(headers, data_rows, header_to_field)

        validation = ImportService.validate_data(node_type_slug, parsed_rows)

        preview_rows = parsed_rows[:10]
        preview_display = []
        for row in preview_rows:
            display_row = {}
            for header in headers:
                field_name = header_to_field.get(header)
                display_row[header] = row.get(field_name, "") if field_name else ""
            preview_display.append(display_row)

        request.session["import_data"] = {
            "filename": filename,
            "format": format,
            "headers": headers,
            "rows": parsed_rows,
            "total_count": len(parsed_rows),
        }

        return json_success(
            data={
                "filename": filename,
                "total_rows": len(parsed_rows),
                "headers": headers,
                "preview": preview_display,
                "valid_count": validation["valid_count"],
                "error_count": validation["error_count"],
                "errors": [
                    {"row": e["row"], "message": "; ".join(e["errors"]) if e["errors"] else "未知错误"}
                    for e in validation["errors"][:20]
                ],
            }
        )

    except Exception as e:
        return json_error(f"文件读取失败：{e!s}", 500)


@login_required
@require_POST
@permission_required("importexport.view")
def do_import(request, node_type_slug):
    """执行导入"""
    node_type, response = _get_node_type_or_redirect(node_type_slug, "importexport:import_list")
    if response:
        return response

    import_data = request.session.get("import_data")
    if not import_data:
        messages.error(request, "请先上传文件")
        return redirect("importexport:import_page", node_type_slug)

    rows = import_data.get("rows", [])

    if not rows:
        messages.error(request, "没有可导入的数据")
        return redirect("importexport:import_page", node_type_slug)

    validation = ImportService.validate_data(node_type_slug, rows)
    valid_rows = [row for i, row in enumerate(rows, 1) if not any(e["row"] == i for e in validation["errors"])]

    try:
        with transaction.atomic():
            result = ImportService.import_data(node_type_slug, valid_rows, request.user, skip_duplicates=True)
    except Exception as e:
        messages.error(request, f"导入失败: {e!s}")
        return redirect("importexport:import_page", node_type_slug)

    total_count = import_data.get("total_count", 0)

    raw_errors = [
        {"row": e["row"], "errors": e.get("errors", []), "data": str(e.get("data", ""))} for e in result["errors"]
    ]
    result_for_template = {
        "total_count": total_count,
        "success_count": result["success_count"],
        "skipped_count": 0,
        "failed_count": result["error_count"],
        "errors": [
            {"row": e["row"], "message": e["errors"][0] if e["errors"] else "未知错误"} for e in result["errors"]
        ],
    }

    del request.session["import_data"]
    request.session["import_errors"] = json.dumps(raw_errors)

    return render(
        request,
        "importexport/import_result.html",
        {
            "node_type": node_type,
            "result": result_for_template,
            "active_section": "import",
        },
    )


@permission_required("importexport.view")
def download_errors(request, node_type_slug):
    """下载错误列表"""
    _node_type, response = _get_node_type_or_redirect(node_type_slug, "importexport:import_list")
    if response:
        return response

    errors_json = request.session.get("import_errors", "[]")
    try:
        errors = json.loads(errors_json)
    except (json.JSONDecodeError, TypeError):
        errors = []

    fields = ImportService.get_importable_fields(node_type_slug)

    return ImportService.generate_error_csv(errors, fields)
