# Core Node Module Routes
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services.node.node_type_service import NodeTypeService

node_bp = Blueprint('node', __name__, url_prefix='/nodes')

@node_bp.before_request
def require_admin():
    """要求管理员权限"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # 节点类型管理需要管理员权限
    if request.endpoint and request.endpoint.startswith('node.node_type'):
        if not current_user.is_admin:
            flash('仅管理员可访问节点类型管理', 'danger')
            return redirect(url_for('node.dashboard'))

@node_bp.route('/')
@login_required
def dashboard():
    """Node Dashboard - 显示所有已启用的节点类型"""
    node_types = NodeTypeService.get_all()
    return render_template('core/node/dashboard.html', node_types=node_types)

@node_bp.route('/admin/node-types')
@login_required
def node_type_admin():
    """节点类型管理页面"""
    node_types = NodeTypeService.get_all_including_inactive()
    node_counts = {}
    for nt in node_types:
        node_counts[nt.id] = NodeTypeService.get_node_count(nt.id)
    return render_template('core/node/node_type_admin.html', 
                           node_types=node_types, 
                           node_counts=node_counts)

@node_bp.route('/admin/node-types/<int:node_type_id>/enable', methods=['POST'])
@login_required
def node_type_enable(node_type_id):
    """启用节点类型"""
    NodeTypeService.enable(node_type_id)
    flash('节点类型已启用', 'success')
    return redirect(url_for('node.node_type_admin'))

@node_bp.route('/admin/node-types/<int:node_type_id>/disable', methods=['POST'])
@login_required
def node_type_disable(node_type_id):
    """禁用节点类型"""
    node_count = NodeTypeService.get_node_count(node_type_id)
    if node_count > 0:
        flash(f'该节点类型下仍有 {node_count} 条数据，无法禁用', 'danger')
    else:
        NodeTypeService.disable(node_type_id)
        flash('节点类型已禁用', 'success')
    return redirect(url_for('node.node_type_admin'))

@node_bp.route('/admin/node-types/<int:node_type_id>/delete', methods=['POST'])
@login_required
def node_type_delete(node_type_id):
    """删除节点类型"""
    node_count = NodeTypeService.get_node_count(node_type_id)
    if node_count > 0:
        flash(f'该节点类型下仍有 {node_count} 条数据，无法删除', 'danger')
    else:
        NodeTypeService.delete(node_type_id)
        flash('节点类型已删除', 'success')
    return redirect(url_for('node.node_type_admin'))

@node_bp.route('/admin/node-types/<int:node_type_id>/settings')
@login_required
def node_type_settings(node_type_id):
    """节点类型设置页面"""
    node_type = NodeTypeService.get_by_id(node_type_id)
    if not node_type:
        flash('节点类型不存在', 'danger')
        return redirect(url_for('node.node_type_admin'))
    node_count = NodeTypeService.get_node_count(node_type_id)
    return render_template('core/node/node_type_settings.html', 
                           node_type=node_type,
                           node_count=node_count)
