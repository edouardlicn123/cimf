# app/modules/core/workspace/routes.py
# 功能说明：工作台/仪表盘模块路由集合

from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from datetime import datetime

workspace_bp = Blueprint('workspace', __name__)


@workspace_bp.before_request
@login_required
def require_login():
    """所有工作台路由默认要求登录"""
    pass


@workspace_bp.route('/', methods=['GET'])
@workspace_bp.route('/index', methods=['GET'])
@workspace_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """系统仪表盘首页"""
    stats = {
        'project_count': 0,
        'active_projects': 0,
        'pending_tasks': 0,
        'unread_notifications': 0,
        'total_volume_m3': 0.0,
        'total_freight_usd': 0.0,
    }

    context = {
        'title': '仪表盘 - FFE 项目跟进系统',
        'username': current_user.username,
        'nickname': current_user.nickname or current_user.username,
        'is_admin': current_user.is_admin,
        'last_login': (
            current_user.last_login_at.strftime('%Y-%m-%d %H:%M:%S')
            if current_user.last_login_at else '首次登录'
        ),
        'current_time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'stats': stats,
    }

    if not current_user.last_login_at:
        flash(
            '欢迎首次登录！建议前往"设置"完善昵称、邮箱和偏好。',
            'info'
        )

    return render_template('core/main/dashboard.html', **context)


@workspace_bp.route('/about', methods=['GET'])
def about():
    """关于系统页面"""
    return render_template(
        'core/main/about.html',
        title='关于系统'
    )


@workspace_bp.route('/help', methods=['GET'])
def help_page():
    """帮助中心页面"""
    return render_template(
        'core/main/help.html',
        title='帮助中心'
    )
