# -*- coding: utf-8 -*-
"""
================================================================================
文件：app/modules/core/cron/admin_routes.py
路径：/home/edo/cimf-v2/app/modules/core/cron/admin_routes.py
================================================================================

功能说明：
    Cron 调度管理后台路由，提供任务管理的 Web 界面。
    
    主要功能：
    - 显示任务管理页面 /admin/cron
    
    页面功能：
    - 显示所有任务列表
    - 显示任务状态（启用/禁用、运行间隔、上次运行时间等）
    - 提供手动触发按钮
    - 提供启用/禁用开关

用法：
    访问 URL：/admin/cron
    需要管理员权限

版本：
    - 1.0: 初始版本

依赖：
    - Flask Blueprint: 路由蓝图
    - CronService: 任务调度服务
"""

from flask import Blueprint, render_template

# 创建管理后台 Blueprint
admin_cron_bp = Blueprint('admin_cron', __name__, url_prefix='/admin')


# =============================================================================
# 页面路由
# =============================================================================

@admin_cron_bp.route('/cron')
def cron_manager():
    """
    Cron 调度管理页面
    
    说明：
        显示所有已注册任务的状态和管理界面。
        页面包含：
        - 任务名称和描述
        - 启用/禁用开关
        - 运行间隔
        - 上次运行时间
        - 下次运行时间
        - 运行状态（成功/失败）
        - 运行次数
        - 错误信息
        - 立即执行按钮
    
    返回：
        渲染的 HTML 模板
    """
    # 获取 Cron 服务
    from app.services.core.cron_service import get_cron_service
    
    cron = get_cron_service()
    status = cron.get_status()
    
    # 任务描述映射
    task_descriptions = {
        'time_sync': '时间同步任务 - 定时与远程时间服务器同步',
        'cache_cleanup': '缓存清理任务 - 清理过期的系统缓存',
    }
    
    # 为每个任务添加描述
    for task in status['tasks'].values():
        task['description'] = task_descriptions.get(task['name'], '未知任务')
    
    # 渲染模板
    return render_template('core/admin/cron_manager.html', cron_status=status)
