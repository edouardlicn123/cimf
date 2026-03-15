# 文件路径：app/modules/core/cron/admin_routes.py
# 功能说明：Cron 调度管理后台路由
# 版本：1.0
# 创建日期：2026-03-14

from flask import Blueprint, render_template

admin_cron_bp = Blueprint('admin_cron', __name__, url_prefix='/admin')


@admin_cron_bp.route('/cron')
def cron_manager():
    """Cron 调度管理页面"""
    from app.services.core.cron_service import get_cron_service
    
    cron = get_cron_service()
    status = cron.get_status()
    
    task_descriptions = {
        'time_sync': '时间同步任务 - 定时与远程时间服务器同步',
        'cache_cleanup': '缓存清理任务 - 清理过期的系统缓存',
    }
    
    for task in status['tasks'].values():
        task['description'] = task_descriptions.get(task['name'], '未知任务')
    
    return render_template('core/admin/cron_manager.html', cron_status=status)
