# Customer Routes
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services.node.customer import CustomerService

customer_bp = Blueprint('customer', __name__, url_prefix='/nodes/customer')

@customer_bp.route('/')
@login_required
def index():
    """客户列表"""
    page = request.args.get('page', 1, type=int)
    pagination = CustomerService.get_customer_list(page=page)
    return render_template('nodes/customer/list.html', 
                         customers=pagination.items,
                         pagination=pagination)

@customer_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """新建客户"""
    from app.modules.nodes.customer.forms import CustomerForm
    from app.modules.core.taxonomy.service import TaxonomyService
    
    # 获取客户类型选项
    taxonomy = TaxonomyService.get_taxonomy_by_slug('customer_type')
    customer_types = TaxonomyService.get_items(taxonomy.id) if taxonomy else []
    form = CustomerForm()
    form.customer_type.choices = [(0, '-- 请选择 --')] + [(t.id, t.name) for t in customer_types]
    
    if form.validate_on_submit():
        data = {
            'customer_name': form.customer_name.data,
            'contact_person': form.contact_person.data,
            'phone': form.phone.data,
            'email': form.email.data,
            'address': form.address.data,
            'customer_type': form.customer_type.data,
            'notes': form.notes.data,
        }
        CustomerService.create_customer(data, current_user.id)
        flash('客户创建成功', 'success')
        return redirect(url_for('customer.index'))
    
    return render_template('nodes/customer/edit.html', form=form, action='create')

@customer_bp.route('/<int:customer_id>')
@login_required
def view(customer_id):
    """查看客户"""
    result = CustomerService.get_customer_by_id(customer_id)
    if not result:
        flash('客户不存在', 'danger')
        return redirect(url_for('customer.index'))
    return render_template('nodes/customer/view.html', node=result['node'], fields=result['fields'])

@customer_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(customer_id):
    """编辑客户"""
    from app.modules.nodes.customer.forms import CustomerForm
    from app.modules.core.taxonomy.service import TaxonomyService
    
    result = CustomerService.get_customer_by_id(customer_id)
    if not result:
        flash('客户不存在', 'danger')
        return redirect(url_for('customer.index'))
    
    taxonomy = TaxonomyService.get_taxonomy_by_slug('customer_type')
    customer_types = TaxonomyService.get_items(taxonomy.id) if taxonomy else []
    form = CustomerForm(data=result['fields'].__dict__ if result['fields'] else {})
    form.customer_type.choices = [(0, '-- 请选择 --')] + [(t.id, t.name) for t in customer_types]
    
    if form.validate_on_submit():
        data = {
            'customer_name': form.customer_name.data,
            'contact_person': form.contact_person.data,
            'phone': form.phone.data,
            'email': form.email.data,
            'address': form.address.data,
            'customer_type': form.customer_type.data,
            'notes': form.notes.data,
        }
        CustomerService.update_customer(customer_id, data, current_user.id)
        flash('客户更新成功', 'success')
        return redirect(url_for('customer.view', customer_id=customer_id))
    
    return render_template('nodes/customer/edit.html', form=form, action='edit', node=result['node'], fields=result['fields'])

@customer_bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete(customer_id):
    """删除客户"""
    CustomerService.delete_customer(customer_id)
    flash('客户已删除', 'success')
    return redirect(url_for('customer.index'))
