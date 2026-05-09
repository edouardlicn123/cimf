# -*- coding: utf-8 -*-
"""
健康检查视图模块
"""

import time
import os
from django.http import JsonResponse
from django.db import connection
from django.utils import timezone
from django.core.cache import cache
from core.decorators import login_required


@login_required
def health_check(request):
    """系统健康检查端点
    
    检查项：
    - status: 总状态 (ok/degraded/error)
    - version: 版本号
    - database: 数据库连接
    - cache: 缓存可用性
    - storage: 存储目录
    - uptime_ms: 检查耗时
    """
    start_time = time.time()
    
    checks = {
        'status': 'ok',
        'version': '1.0.0',
        'timestamp': timezone.now().isoformat(),
    }
    overall_status = 'ok'
    
    try:
        connection.ensure_connection()
        checks['database'] = 'ok'
    except Exception as e:
        checks['database'] = f'error: {str(e)}'
        overall_status = 'error'
    
    try:
        cache.set('_health_check', 'ok', 10)
        if cache.get('_health_check') == 'ok':
            checks['cache'] = 'ok'
        else:
            checks['cache'] = 'degraded'
            overall_status = 'degraded'
    except Exception as e:
        checks['cache'] = f'error: {str(e)}'
        overall_status = 'degraded'
    
    try:
        storage_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage')
        if os.path.exists(storage_path):
            checks['storage'] = 'ok'
        else:
            checks['storage'] = 'missing'
            overall_status = 'degraded'
    except Exception as e:
        checks['storage'] = f'error: {str(e)}'
        overall_status = 'degraded'
    
    checks['uptime_ms'] = round((time.time() - start_time) * 1000, 2)
    checks['status'] = overall_status
    
    status_code = 200 if overall_status == 'ok' else 503
    return JsonResponse(checks, status=status_code)


@login_required
def detailed_health_check(request):
    """详细健康检查端点"""
    start_time = time.time()
    
    checks = {
        'status': 'ok',
        'version': '1.0.0',
    }
    overall_status = 'ok'
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks['database'] = 'ok'
    except Exception as e:
        checks['database'] = f'error: {str(e)}'
        overall_status = 'error'
    
    try:
        from core.models import User, SystemSetting
        checks['tables'] = {
            'users': User.objects.count(),
            'settings': SystemSetting.objects.count(),
        }
    except Exception as e:
        checks['tables'] = f'error: {str(e)}'
        overall_status = 'degraded'
    
    try:
        from core.node.models import NodeType, Node
        checks['modules'] = {
            'node_types': NodeType.objects.count(),
            'nodes': Node.objects.count(),
        }
    except Exception as e:
        checks['modules'] = f'error: {str(e)}'
    
    try:
        storage_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage')
        if os.path.exists(storage_path):
            checks['storage'] = 'ok'
            try:
                stat = os.statvfs(storage_path)
                free_space = stat.f_bavail * stat.f_frsize / (1024**3)
                checks['disk_free_gb'] = round(free_space, 2)
            except Exception:
                pass
        else:
            checks['storage'] = 'missing'
            overall_status = 'degraded'
    except Exception as e:
        checks['storage'] = f'error: {str(e)}'
    
    checks['uptime_ms'] = round((time.time() - start_time) * 1000, 2)
    checks['status'] = overall_status
    
    status_code = 200 if overall_status == 'ok' else 503
    return JsonResponse(checks, status=status_code)


@login_required
def api_version(request):
    """API 版本信息"""
    return JsonResponse({
        'version': '1.0.0',
        'api_version': 'v1',
        'build_date': '2026-04-09',
    })