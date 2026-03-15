# -*- coding: utf-8 -*-
"""
================================================================================
文件：app/modules/core/cron/routes.py
路径：/home/edo/cimf-v2/app/modules/core/cron/routes.py
================================================================================

功能说明：
    Cron 任务调度 API 路由，提供任务管理的 HTTP 接口。
    
    主要功能：
    - 获取所有任务状态：GET /api/cron/status
    - 手动触发任务：POST /api/cron/run/<task_name>
    - 切换任务状态：POST /api/cron/toggle/<task_name>
    
    说明：
        这些 API 供前端 JavaScript 调用，实现任务的手动触发和状态切换。

用法：
    1. 获取任务状态：
        GET /api/cron/status
        返回：{running: true, tasks: {...}}
    
    2. 手动触发任务：
        POST /api/cron/run/time_sync
        返回：{success: true, task: 'time_sync', status: 'success'}
    
    3. 切换任务状态：
        POST /api/cron/toggle/cache_cleanup
        Body: {enabled: false}
        返回：{success: true, task: 'cache_cleanup', enabled: false}

版本：
    - 1.0: 初始版本
    - 1.1: 添加装饰器统一错误处理

依赖：
    - CronService: 任务调度服务
    - Flask Blueprint: 路由蓝图
"""

import logging
from functools import wraps
from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

# 创建 Blueprint
cron_bp = Blueprint('cron', __name__, url_prefix='/api/cron')


# =============================================================================
# 装饰器
# =============================================================================

def handle_cron_error(func):
    """
    统一错误处理装饰器
    
    说明：
        捕获函数中的异常，返回格式化的错误响应。
        避免每个路由重复编写 try-except。
    
    参数：
        func: 要包装的函数
        
    返回：
        包装后的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__} 执行失败: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    return wrapper


# =============================================================================
# API 路由
# =============================================================================

@cron_bp.route('/status', methods=['GET'])
def cron_status():
    """
    获取所有任务状态
    
    说明：
        返回调度器的运行状态和所有已注册任务的状态信息。
        
    返回：
        JSON 对象，包含：
        - running: 调度器是否运行中
        - start_time: 启动时间
        - tasks: 任务状态字典
    """
    from app.services.core.cron_service import get_cron_service
    cron = get_cron_service()
    return jsonify(cron.get_status())


@cron_bp.route('/run/<path:task_name>', methods=['POST'])
@handle_cron_error
def cron_run_task(task_name):
    """
    手动触发任务
    
    说明：
        立即执行指定任务，不受调度间隔限制。
        用于管理员手动执行任务。
        
    参数：
        task_name: 任务名称（URL 路径参数）
        
    返回：
        JSON 对象，包含：
        - success: 是否成功
        - task: 任务名称
        - status: 执行状态
        - last_run: 上次运行时间
    """
    from app.services.core.cron_service import get_cron_service
    cron = get_cron_service()
    result = cron.trigger(task_name)
    return jsonify(result)


@cron_bp.route('/toggle/<path:task_name>', methods=['POST'])
@handle_cron_error
def cron_toggle_task(task_name):
    """
    切换任务启用状态
    
    说明：
        动态启用或禁用任务。
        状态会保存到系统设置中，持久化保存。
        
    参数：
        task_name: 任务名称（URL 路径参数）
        
    请求体：
        JSON 对象：{enabled: true/false}
        
    返回：
        JSON 对象，包含：
        - success: 是否成功
        - task: 任务名称
        - enabled: 新的启用状态
    """
    from app.services.core.cron_service import get_cron_service
    data = request.get_json() or {}
    enabled = data.get('enabled', True)
    cron = get_cron_service()
    result = cron.toggle(task_name, enabled)
    return jsonify(result)
