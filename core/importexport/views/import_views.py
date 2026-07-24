import json
import logging

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from core.decorators import login_required_json, permission_required
from core.importexport import ImportService, TemplateGenerator
from core.node.services import NodeTypeService
from core.utils.response import json_error, json_success

from .export_views import _get_node_type_or_redirect

logger = logging.getLogger(__name__)


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


@require_GET
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

    from core.utils.response import validate_upload  # noqa: PLC0415

    valid, error_msg = validate_upload(file, max_size=10 * 1024 * 1024, allowed_exts=[".csv", ".xlsx", ".xls"])
    if not valid:
        return json_error(error_msg, 400)

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
        logger.exception(f"文件读取失败: filename={filename}")
        return json_error(f"文件读取失败：{e!s}", 500)


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
        logger.exception(f"导入失败: node_type={node_type_slug}")
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


@require_GET
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
