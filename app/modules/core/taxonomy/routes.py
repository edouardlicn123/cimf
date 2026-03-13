# 文件路径：app/modules/taxonomy/routes.py
# 功能说明：Taxonomy 词汇表路由

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.services import PermissionService
from app.modules.core.taxonomy.service import TaxonomyService
from app.modules.core.taxonomy.forms import TaxonomyForm, TaxonomyItemForm
from app.modules.core.fields import FIELD_TYPES

taxonomy_bp = Blueprint('taxonomy', __name__, url_prefix='/nodes')


@taxonomy_bp.route('/field-types', methods=['GET'])
def field_types():
    """字段类型列表"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if not current_user.is_admin:
        flash('仅管理员可访问字段类型', 'danger')
        return redirect(url_for('workspace.dashboard'))
    
    field_types_list = []
    for name, field_class in FIELD_TYPES.items():
        field_instance = field_class.__new__(field_class)
        field_types_list.append({
            'name': name,
            'label': getattr(field_class, 'label', name),
            'widget': getattr(field_class, 'widget', ''),
            'properties': getattr(field_class, 'properties', []),
        })
    
    return render_template('core/content_structure/field_types.html', field_types=field_types_list)


@taxonomy_bp.route('/content-structure', methods=['GET'])
def content_structure_dashboard():
    """内容结构管理首页"""
    if not current_user.is_admin:
        flash('仅管理员可访问内容结构', 'danger')
        return redirect(url_for('workspace.dashboard'))
    
    taxonomies = TaxonomyService.get_all_taxonomies()
    field_types_count = len(FIELD_TYPES)
    return render_template('core/content_structure/content_structure_dashboard.html', 
                          taxonomies_count=len(taxonomies),
                          field_types_count=field_types_count)


@taxonomy_bp.before_request
def require_login():
    """要求登录"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))


@taxonomy_bp.route('', methods=['GET'])
def index():
    """词汇表列表"""
    if not current_user.is_admin:
        flash('仅管理员可访问词汇表', 'danger')
        return redirect(url_for('workspace.dashboard'))
    
    taxonomies = TaxonomyService.get_all_taxonomies()
    return render_template('core/content_structure/taxonomies.html', taxonomies=taxonomies)


@taxonomy_bp.route('/new', methods=['GET', 'POST'])
def create():
    """创建词汇表"""
    if not current_user.is_admin:
        flash('仅管理员可访问词汇表', 'danger')
        return redirect(url_for('workspace.dashboard'))
    
    form = TaxonomyForm()
    
    if form.validate_on_submit():
        TaxonomyService.create_taxonomy({
            'name': form.name.data,
            'slug': form.slug.data,
            'description': form.description.data
        })
        flash('词汇表创建成功', 'success')
        return redirect(url_for('taxonomy.index'))
    
    return render_template('core/content_structure/taxonomy_edit.html', form=form, action='create')


@taxonomy_bp.route('/<int:taxonomy_id>', methods=['GET'])
def view(taxonomy_id):
    """查看词汇表及词汇项"""
    if not current_user.is_admin:
        flash('仅管理员可访问词汇表', 'danger')
        return redirect(url_for('workspace.dashboard'))
    
    taxonomy = TaxonomyService.get_taxonomy_by_id(taxonomy_id)
    if not taxonomy:
        flash('词汇表不存在', 'danger')
        return redirect(url_for('taxonomy.index'))
    
    items = TaxonomyService.get_items(taxonomy_id)
    return render_template('core/content_structure/taxonomy_view.html', taxonomy=taxonomy, items=items)


@taxonomy_bp.route('/<int:taxonomy_id>/edit', methods=['GET', 'POST'])
def edit(taxonomy_id):
    """编辑词汇表"""
    if not current_user.is_admin:
        flash('仅管理员可访问词汇表', 'danger')
        return redirect(url_for('workspace.dashboard'))
    
    taxonomy = TaxonomyService.get_taxonomy_by_id(taxonomy_id)
    if not taxonomy:
        flash('词汇表不存在', 'danger')
        return redirect(url_for('taxonomy.index'))
    
    form = TaxonomyForm(obj=taxonomy)
    
    if form.validate_on_submit():
        TaxonomyService.update_taxonomy(taxonomy_id, {
            'name': form.name.data,
            'slug': form.slug.data,
            'description': form.description.data
        })
        flash('词汇表更新成功', 'success')
        return redirect(url_for('taxonomy.index'))
    
    return render_template('core/content_structure/taxonomy_edit.html', form=form, action='edit', taxonomy=taxonomy)


@taxonomy_bp.route('/<int:taxonomy_id>/delete', methods=['POST'])
def delete(taxonomy_id):
    """删除词汇表"""
    if not current_user.is_admin:
        flash('仅管理员可访问词汇表', 'danger')
        return redirect(url_for('workspace.dashboard'))
    
    if TaxonomyService.delete_taxonomy(taxonomy_id):
        flash('词汇表删除成功', 'success')
    else:
        flash('删除失败', 'danger')
    
    return redirect(url_for('taxonomy.index'))


@taxonomy_bp.route('/<int:taxonomy_id>/items', methods=['POST'])
def create_item(taxonomy_id):
    """新增词汇项"""
    if not PermissionService.has_permission(current_user, 'node.taxonomy.manage'):
        return jsonify({'success': False, 'message': '无权管理词汇表'})
    
    form = TaxonomyItemForm()
    
    if form.validate_on_submit():
        item = TaxonomyService.create_item(taxonomy_id, {
            'name': form.name.data,
            'description': form.description.data
        })
        return jsonify({'success': True, 'item': {'id': item.id, 'name': item.name}})
    
    return jsonify({'success': False, 'message': '表单验证失败'})


@taxonomy_bp.route('/<int:taxonomy_id>/items/<int:item_id>', methods=['PUT'])
def update_item(taxonomy_id, item_id):
    """更新词汇项"""
    if not PermissionService.has_permission(current_user, 'node.taxonomy.manage'):
        return jsonify({'success': False, 'message': '无权管理词汇表'})
    
    form = TaxonomyItemForm()
    
    if form.validate_on_submit():
        item = TaxonomyService.update_item(item_id, {
            'name': form.name.data,
            'description': form.description.data
        })
        if item:
            return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': '更新失败'})


@taxonomy_bp.route('/<int:taxonomy_id>/items/<int:item_id>', methods=['DELETE'])
def delete_item(taxonomy_id, item_id):
    """删除词汇项"""
    if not PermissionService.has_permission(current_user, 'node.taxonomy.manage'):
        return jsonify({'success': False, 'message': '无权管理词汇表'})
    
    if TaxonomyService.delete_item(item_id):
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': '删除失败'})
