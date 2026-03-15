# 文件路径：app/modules/core/cron/routes.py
# 功能说明：Cron 任务调度 API 路由
# 版本：1.1
# 创建日期：2026-03-14
# 更新日期：2026-03-15

import logging
from functools import wraps
from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)
cron_bp = Blueprint('cron', __name__, url_prefix='/api/cron')


def handle_cron_error(func):
    """统一错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__} 执行失败: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    return wrapper


@cron_bp.route('/status', methods=['GET'])
def cron_status():
    """获取所有任务状态"""
    from app.services.core.cron_service import get_cron_service
    cron = get_cron_service()
    return jsonify(cron.get_status())


@cron_bp.route('/run/<path:task_name>', methods=['POST'])
@handle_cron_error
def cron_run_task(task_name):
    """手动触发任务"""
    from app.services.core.cron_service import get_cron_service
    cron = get_cron_service()
    result = cron.trigger(task_name)
    return jsonify(result)


@cron_bp.route('/toggle/<path:task_name>', methods=['POST'])
@handle_cron_error
def cron_toggle_task(task_name):
    """切换任务启用状态"""
    from app.services.core.cron_service import get_cron_service
    data = request.get_json() or {}
    enabled = data.get('enabled', True)
    cron = get_cron_service()
    result = cron.toggle(task_name, enabled)
    return jsonify(result)
