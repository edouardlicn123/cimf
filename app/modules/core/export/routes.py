# app/modules/export/routes.py
# 功能说明：导出功能模块，支持 Excel、CSV 等格式的报表导出

from flask import Blueprint, Response, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from datetime import datetime
import io
import csv
from typing import Dict, Any, List, Optional

from app.services import SettingsService

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from app.models import User
from app import db

export_bp = Blueprint('export', __name__, url_prefix='/export')


@export_bp.before_request
@login_required
def require_login():
    """所有导出路由都需要登录"""
    pass


def get_watermark_info() -> Optional[str]:
    """获取导出文件水印信息（使用统一的水印显示内容配置）"""
    try:
        enable_watermark = SettingsService.get_setting('enable_export_watermark')
        if enable_watermark is True or enable_watermark == 'true':
            pass
        else:
            return None
        
        # 获取水印显示内容配置（与网页水印一致）
        wm_content_str = SettingsService.get_setting('web_watermark_content') or 'username,system_name,datetime'
        wm_content_list = wm_content_str.split(',')
        
        watermark_parts = []
        
        # 用户名
        if 'username' in wm_content_list:
            watermark_parts.append(current_user.username)
        
        # 系统名
        if 'system_name' in wm_content_list:
            system_name = SettingsService.get_setting('system_name') or 'CIMF'
            watermark_parts.append(system_name)
        
        # 时间
        if 'datetime' in wm_content_list:
            from app.services.core.time_service import TimeService
            watermark_parts.append(TimeService.get_current_time())
        
        # 自定义文字
        if 'custom' in wm_content_list:
            custom_text = SettingsService.get_setting('web_watermark_custom_text')
            if custom_text:
                watermark_parts.append(custom_text)
        
        if not watermark_parts:
            return None
        
        return "# 水印: " + " | ".join(watermark_parts)
        
    except Exception as e:
        current_app.logger.error(f"获取水印信息失败: {e}")
        return None


def generate_csv(data: list[Dict[str, Any]], filename: str, add_watermark: bool = True) -> Response:
    """生成 CSV 响应"""
    output = io.StringIO()
    
    if add_watermark:
        watermark = get_watermark_info()
        if watermark:
            output.write(watermark + '\n')
    
    writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
    writer.writeheader()
    writer.writerows(data)

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'text/csv; charset=utf-8-sig'
        }
    )


@export_bp.route('/users.csv', methods=['GET'])
@login_required
def export_users_csv():
    """导出用户列表（仅管理员）"""
    if not current_user.is_admin:
        flash('只有管理员可以导出用户数据', 'danger')
        return redirect(url_for('workspace.dashboard'))

    users = User.query.all()
    if not users:
        flash('暂无用户数据可导出', 'info')
        return redirect(url_for('admin.system_users'))

    data = [
        {
            'ID': u.id,
            '用户名': u.username,
            '昵称': u.nickname or '',
            '邮箱': u.email or '',
            '是否管理员': '是' if u.is_admin else '否',
            '是否启用': '是' if u.is_active else '否',
            '最后登录': u.last_login_at.strftime('%Y-%m-%d %H:%M:%S') if u.last_login_at else '从未登录',
            '创建时间': u.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for u in users
    ]

    filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return generate_csv(data, filename)


@export_bp.route('/calculator-result', methods=['POST'])
@login_required
def export_calculator_result():
    """从计算器页面导出结果"""
    result_data = request.json or {}
    if not result_data:
        flash('没有可导出的计算结果', 'warning')
        return redirect(request.referrer or url_for('workspace.dashboard'))

    flat_data = [
        {'项目名称': result_data.get('project_name', ''),
         '柜数': result_data.get('container_count', 1),
         '单柜 DDP': result_data.get('ddp_per_container', 0),
         '总价 USD': result_data.get('total_ddp', 0),
         '导出时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ]

    filename = f"calculator_result_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return generate_csv(flat_data, filename)


@export_bp.errorhandler(403)
def forbidden(e):
    flash('无权限访问该导出功能', 'danger')
    return redirect(url_for('workspace.dashboard'))
