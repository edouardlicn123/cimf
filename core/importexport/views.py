"""
导入导出视图
"""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render

from core.importexport import ExportService, ImportService, TemplateGenerator
from core.node.services import NodeTypeService
from core.services import PermissionService


def _build_filter_summaries(node_type_slug: str, filters: list) -> list:
    """构建过滤器摘要"""
    if not filters:
        return []

    all_fields = ExportService.get_exportable_fields(node_type_slug)
    field_map = {f['name']: f['label'] for f in all_fields}

    summaries = []
    for f in filters:
        field = f.get('field', '')
        value = f.get('value', '')

        if field == 'region':
            try:
                region_data = json.loads(value) if isinstance(value, str) else value
            except (json.JSONDecodeError, TypeError):
                region_data = {}
            parts = [v for v in [region_data.get('province', ''), region_data.get('city', ''), region_data.get('district', '')] if v]
            if parts:
                summaries.append({'label': '省市区', 'value': ' '.join(parts)})
        else:
            label = field_map.get(field, field)
            summaries.append({'label': label, 'value': value})

    return summaries


@login_required
def export_list(request):
    """导出页 - 显示所有模块的导出入口"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return redirect('core:dashboard')

    node_types = NodeTypeService.get_all()
    return render(request, 'importexport/export.html', {
        'node_types': node_types,
        'active_section': 'export',
    })


@login_required
def export_select_fields(request, node_type_slug):
    """字段选择页"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return redirect('core:dashboard')

    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        return redirect('importexport:export_list')

    if request.method == 'POST':
        selected_fields = []
        for key in request.POST:
            if key.startswith('field_'):
                value = request.POST.get(key)
                if value and value.strip():
                    selected_fields.append(value.strip())

        if not selected_fields:
            messages.error(request, '请至少选择一个导出字段')
            return redirect('importexport:export_select_fields', node_type_slug)

        request.session['export_selected_fields'] = selected_fields
        request.session['export_format'] = request.POST.get('format', 'csv')

        filters = []
        for i in range(6):
            f_field = request.POST.get(f'filter_field_{i}', '')
            f_value = request.POST.get(f'filter_value_{i}', '')
            if f_field and f_value:
                filters.append({'field': f_field, 'value': f_value.strip()})

        region_province = request.POST.get('filter_region_province', '')
        region_city = request.POST.get('filter_region_city', '')
        region_district = request.POST.get('filter_region_district', '')
        if region_province or region_city or region_district:
            filters.append({
                'field': 'region',
                'value': json.dumps({
                    'province': region_province,
                    'city': region_city,
                    'district': region_district
                }, ensure_ascii=False)
            })

        request.session['export_filters'] = filters
        return redirect('importexport:export_confirm', node_type_slug)

    fields = ExportService.get_exportable_fields(node_type_slug)
    filterable_fields = ExportService.get_filterable_fields(node_type_slug)
    has_region = ExportService.has_region_field(node_type_slug)

    return render(request, 'importexport/export_fields.html', {
        'node_type': node_type,
        'fields': fields,
        'filterable_fields': filterable_fields,
        'has_region': has_region,
        'active_section': 'export',
    })


@login_required
def export_confirm(request, node_type_slug):
    """确认页"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return redirect('core:dashboard')

    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        return redirect('importexport:export_list')

    selected_fields = request.session.get('export_selected_fields', [])
    export_format = request.session.get('export_format', 'csv')
    filters = request.session.get('export_filters', [])

    if request.method == 'POST':
        return redirect('importexport:export_exporting', node_type_slug)

    if not selected_fields:
        return redirect('importexport:export_select_fields', node_type_slug)

    fields_info = ExportService.get_fields_info(node_type_slug, selected_fields)
    record_count = ExportService.get_record_count(node_type_slug, filters)
    preview_data = ExportService.get_preview(node_type_slug, selected_fields, filters, limit=5)

    filter_summaries = _build_filter_summaries(node_type_slug, filters)

    return render(request, 'importexport/export_confirm.html', {
        'node_type': node_type,
        'selected_fields': selected_fields,
        'fields_info': fields_info,
        'export_format': export_format,
        'record_count': record_count,
        'preview_data': preview_data,
        'filter_summaries': filter_summaries,
        'active_section': 'export',
    })


@login_required
def export_exporting(request, node_type_slug):
    """导出中页"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return redirect('core:dashboard')

    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        return redirect('importexport:export_list')

    selected_fields = request.session.get('export_selected_fields', [])
    if not selected_fields:
        return redirect('importexport:export_select_fields', node_type_slug)

    return render(request, 'importexport/export_exporting.html', {
        'node_type': node_type,
        'active_section': 'export',
    })


@login_required
def do_export(request, node_type_slug):
    """执行导出"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return redirect('core:dashboard')

    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        return redirect('importexport:export_list')

    selected_fields = request.session.get('export_selected_fields', [])
    export_format = request.session.get('export_format', 'csv')
    filters = request.session.get('export_filters', [])

    if not selected_fields:
        return redirect('importexport:export_select_fields', node_type_slug)

    try:
        response = ExportService.export(node_type_slug, selected_fields, export_format, filters)
        del request.session['export_selected_fields']
        del request.session['export_format']
        if 'export_filters' in request.session:
            del request.session['export_filters']
        return response
    except Exception as e:
        messages.error(request, f'导出失败：{e!s}')
        return redirect('importexport:export_select_fields', node_type_slug)


@login_required
def import_list(request):
    """导入页 - 显示所有模块的导入入口"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return redirect('core:dashboard')

    node_types = NodeTypeService.get_all()
    return render(request, 'importexport/import.html', {
        'node_types': node_types,
        'active_section': 'import',
    })


@login_required
def import_page(request, node_type_slug):
    """导入操作页"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return redirect('core:dashboard')

    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        return redirect('importexport:import_list')

    fields = ImportService.get_importable_fields(node_type_slug)

    return render(request, 'importexport/import_page.html', {
        'node_type': node_type,
        'fields': fields,
        'active_section': 'import',
    })


@login_required
def download_template(request, node_type_slug):
    """下载导入模板"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return redirect('core:dashboard')

    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        return redirect('importexport:import_list')

    return TemplateGenerator.generate(node_type_slug)


@login_required
def upload_preview(request, node_type_slug):
    """上传并预览数据 - AJAX"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return JsonResponse({'success': False, 'error': '权限不足'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '需要 POST 请求'}, status=400)

    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        return JsonResponse({'success': False, 'error': '节点类型不存在'}, status=404)

    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'success': False, 'error': '请选择文件'}, status=400)

    filename = file.name

    # 验证文件大小（最大 10MB）
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        return JsonResponse({'success': False, 'error': '文件大小不能超过 10MB'}, status=400)

    # 验证文件扩展名
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        return JsonResponse({'success': False, 'error': '只允许上传 CSV 或 Excel 文件'}, status=400)

    format = 'xlsx' if filename.lower().endswith(('.xlsx', '.xls')) else 'csv'

    try:
        headers, data_rows = ImportService.read_file(file, format)

        if not headers:
            return JsonResponse({'success': False, 'error': '文件为空或格式不正确'}, status=400)

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
                display_row[header] = row.get(field_name, '') if field_name else ''
            preview_display.append(display_row)

        request.session['import_data'] = {
            'filename': filename,
            'format': format,
            'headers': headers,
            'rows': parsed_rows,
            'total_count': len(parsed_rows),
        }

        return JsonResponse({
            'success': True,
            'data': {
                'filename': filename,
                'total_rows': len(parsed_rows),
                'headers': headers,
                'preview': preview_display,
                'valid_count': validation['valid_count'],
                'error_count': validation['error_count'],
                'errors': [
                    {'row': e['row'], 'message': '; '.join(e['errors']) if e['errors'] else '未知错误'}
                    for e in validation['errors'][:20]
                ],
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'文件读取失败：{e!s}'}, status=500)


@login_required
def do_import(request, node_type_slug):
    """执行导入"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return redirect('core:dashboard')

    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        return redirect('importexport:import_list')

    import_data = request.session.get('import_data')
    if not import_data:
        messages.error(request, '请先上传文件')
        return redirect('importexport:import_page', node_type_slug)

    rows = import_data.get('rows', [])

    if not rows:
        messages.error(request, '没有可导入的数据')
        return redirect('importexport:import_page', node_type_slug)

    validation = ImportService.validate_data(node_type_slug, rows)
    valid_rows = [row for i, row in enumerate(rows, 1)
                  if not any(e['row'] == i for e in validation['errors'])]

    try:
        with transaction.atomic():
            result = ImportService.import_data(node_type_slug, valid_rows, request.user, skip_duplicates=True)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'导入失败: {e!s}'
        }, status=500)

    total_count = import_data.get('total_count', 0)

    raw_errors = [
        {'row': e['row'], 'errors': e.get('errors', []), 'data': str(e.get('data', ''))}
        for e in result['errors']
    ]
    result_for_template = {
        'total_count': total_count,
        'success_count': result['success_count'],
        'skipped_count': 0,
        'failed_count': result['error_count'],
        'errors': [
            {'row': e['row'], 'message': e['errors'][0] if e['errors'] else '未知错误'}
            for e in result['errors']
        ]
    }

    del request.session['import_data']
    request.session['import_errors'] = json.dumps(raw_errors)

    return render(request, 'importexport/import_result.html', {
        'node_type': node_type,
        'result': result_for_template,
        'active_section': 'import',
    })


@login_required
def download_errors(request, node_type_slug):
    """下载错误列表"""
    if not PermissionService.has_permission(request.user, 'importexport.view'):
        return redirect('core:dashboard')

    node_type = NodeTypeService.get_by_slug(node_type_slug)
    if not node_type:
        return redirect('importexport:import_list')

    errors_json = request.session.get('import_errors', '[]')
    errors = json.loads(errors_json)

    fields = ImportService.get_importable_fields(node_type_slug)

    return ImportService.generate_error_csv(errors, fields)
