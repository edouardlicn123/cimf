"""
模块管理视图
"""

import logging
from pathlib import Path

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from core.decorators import admin_required
from core.module.services import ModuleService

logger = logging.getLogger(__name__)


@admin_required
def modules_manage(request):
    """模块管理页面 - 卡片式 + 搜索/筛选/分页"""

    search = request.GET.get('search', '').strip()
    type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    page_num = request.GET.get('page', 1)

    registered = ModuleService.get_all()
    all_modules = ModuleService.scan_modules()
    registered_ids = {m.module_id for m in registered}

    for module in registered:
        if module.path:
            module_info = ModuleService._load_module_info(module.path)
            module.dependencies = module_info.get('require', []) if module_info else []
        else:
            module.dependencies = []

    def module_to_dict(m, status, is_registered, error_msg=None):
        if hasattr(m, 'module_id'):
            return {
                'id': m.module_id,
                'name': m.name,
                'module_type': m.module_type,
                'version': m.version,
                'author': m.author,
                'description': m.description,
                'icon': getattr(m, 'icon', 'bi-wrench'),
                '_status': status,
                'is_registered': is_registered,
                'dependencies': getattr(m, 'dependencies', []),
                'path': getattr(m, 'path', None),
                'error': error_msg,
            }
        return {
            'id': m.get('id', ''),
            'name': m.get('name', ''),
            'module_type': m.get('type', ''),
            'version': m.get('version', '1.0.0'),
            'author': m.get('author', ''),
            'description': m.get('description', ''),
            'icon': m.get('icon', 'bi-box-seam'),
            '_status': status,
            'is_registered': is_registered,
            'dependencies': m.get('require', []),
            'path': m.get('path', None),
            'error': error_msg,
        }

    modules_list = []

    for m in registered:
        if m.is_active:
            status = 'active'
        elif m.is_installed:
            status = 'installed'
        else:
            status = 'uninstalled'

        error_msg = None
        if m.path:
            module_path = Path(ModuleService.MODULES_DIR) / m.path
            if not module_path.exists():
                status = 'error'
                error_msg = f'模块目录不存在: {m.path}'

        modules_list.append(module_to_dict(m, status, True, error_msg))

    modules_list.extend(
        module_to_dict(m, 'uninstalled', False)
        for m in all_modules if m['id'] not in registered_ids
    )

    if search:
        modules_list = [m for m in modules_list if search.lower() in m['name'].lower() or search.lower() in m['id'].lower()]

    if type_filter:
        modules_list = [m for m in modules_list if m['module_type'] == type_filter]

    if status_filter:
        modules_list = [m for m in modules_list if m['_status'] == status_filter]

    status_order = {'active': 0, 'installed': 1, 'uninstalled': 2, 'error': 3}
    modules_list.sort(key=lambda m: (status_order.get(m['_status'], 99), m['module_type'], m['name']))

    paginator = Paginator(modules_list, 12)
    page_obj = paginator.get_page(page_num)

    base_query = '?'
    params = []
    if search:
        params.append(f'search={search}')
    if type_filter:
        params.append(f'type={type_filter}')
    if status_filter:
        params.append(f'status={status_filter}')
    base_query = '&' + '&'.join(params) + '&' if params else '?'

    start = max(1, page_obj.number - 2)
    end = min(paginator.num_pages, page_obj.number + 2)
    page_range = range(start, end + 1)

    return render(request, 'module/modules.html', {
        'modules': page_obj,
        'page_obj': page_obj,
        'page_range': page_range,
        'current_page': page_obj.number,
        'base_query': base_query,
        'search': search,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'active_section': 'modules_manage',
    })


@require_POST
@admin_required
def module_scan(request):
    """扫描并注册模块"""
    result = ModuleService.scan_register_install(do_install=True, dry_run=False, respect_install_on_init=False)

    msg_parts = []
    if result.get('registered', 0) > 0:
        msg_parts.append(f"注册 {result['registered']} 个新模块")
    if result.get('installed', 0) > 0:
        msg_parts.append(f"安装 {result['installed']} 个模块")
    if result.get('skipped', 0) > 0:
        msg_parts.append(f"跳过 {result['skipped']} 个模块")

    if msg_parts:
        messages.success(request, f"扫描完成: {', '.join(msg_parts)}")
    else:
        messages.info(request, "扫描完成: 没有新模块")

    if result.get('failed'):
        for fail in result['failed']:
            messages.error(request, f"失败: {fail}")

    return redirect('module:list')


@require_POST
@admin_required
def module_install(request, module_id: str):
    """安装模块"""
    success, message = ModuleService.install_module(module_id)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect('module:list')


@require_POST
@admin_required
def module_enable(request, module_id: str):
    """启用模块"""
    success = ModuleService.enable_module(module_id)
    status = '启用' if success else '启用失败'
    messages.success(request, f'模块已{status}')
    return redirect('module:list')


@require_POST
@admin_required
def module_disable(request, module_id: str):
    """禁用模块"""
    success = ModuleService.disable_module(module_id)
    status = '禁用' if success else '禁用失败'
    messages.success(request, f'模块已{status}')
    return redirect('module:list')


@admin_required
def module_create(request):
    """模块创建页面"""
    return render(request, 'module/modules/create.html', {
        'active_section': 'modules',
        'csrf_token_value': get_token(request),
    })


@admin_required
@require_POST
def module_create_action(request):
    """创建模块"""
    name = request.POST.get('name', '').strip()
    module_id = request.POST.get('module_id', '').strip()
    module_type = request.POST.get('module_type', 'node').strip()
    description = request.POST.get('description', '').strip()

    if not name or not module_id:
        return JsonResponse({'success': False, 'error': '名称和标识不能为空'})

    try:
        ModuleService.create_module(module_id, name, module_type, description)
        return JsonResponse({'success': True, 'message': '模块创建成功'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
