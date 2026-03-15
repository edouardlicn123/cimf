# app/modules/core/admin/routes.py
# 功能说明：后台管理模块路由集合

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.forms.admin_forms import UserSearchForm, UserForm, SystemSettingsForm, PermissionForm, RoleNameForm
from app.services import UserService, SettingsService, PermissionService, UserRole
from werkzeug.exceptions import Forbidden

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
@login_required
def require_admin():
    """所有后台路由要求登录且必须是管理员或组长"""
    if not PermissionService.can_access_admin(current_user):
        flash('需要管理员或组长权限访问该页面', 'danger')
        return redirect(url_for('workspace.dashboard'))


@admin_bp.route('/dashboard', methods=['GET'])
def admin_dashboard():
    """后台仪表盘 - 重定向到系统设置页面"""
    return redirect(url_for('admin.system_settings'))


@admin_bp.route('/system-users', methods=['GET'])
def system_users():
    """系统用户列表页面"""
    form = UserSearchForm(request.args)

    search_term = form.username.data if form.username.data else None
    only_active = form.is_active.data if form.is_active.data is not None else True

    try:
        users = UserService.get_user_list(
            search_term=search_term,
            only_active=only_active
        )
        return render_template('core/admin/system_users.html', users=users, form=form, active_section='users')
    except Exception as e:
        current_app.logger.error(f"加载用户列表失败: {str(e)}", exc_info=True)
        flash(f'加载用户列表失败：{str(e)}', 'danger')
        return render_template('core/admin/system_users.html', users=[], form=form, active_section='users')


@admin_bp.route('/system-user/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_bp.route('/system-user/create', methods=['GET', 'POST'], defaults={'user_id': None})
def user_edit(user_id=None):
    """用户编辑 / 新建页面"""
    is_edit = user_id is not None

    user = None
    if is_edit:
        user = UserService.get_user_by_id(user_id)
        if not user:
            flash('用户不存在或无权限访问', 'danger')
            return redirect(url_for('admin.system_users'))

    form = UserForm(
        obj=user,
        is_edit=is_edit,
        original_username=user.username if user else None,
        original_email=user.email if user else None,
        user_id=user_id
    )

    if form.validate_on_submit():
        try:
            if is_edit:
                UserService.update_user(
                    user_id=user_id,
                    username=form.username.data,
                    nickname=form.nickname.data,
                    email=form.email.data,
                    password=form.password.data if form.password.data else None,
                    role=form.role.data,
                    is_admin=form.is_admin.data,
                    is_active=form.is_active.data
                )
                flash('用户信息更新成功', 'success')
            else:
                UserService.create_user(
                    username=form.username.data,
                    nickname=form.nickname.data,
                    email=form.email.data,
                    password=form.password.data,
                    role=form.role.data,
                    is_admin=form.is_admin.data
                )
                flash('新用户创建成功', 'success')

            return redirect(url_for('admin.system_users'))

        except ValueError as ve:
            flash(str(ve), 'danger')
        except PermissionError:
            flash('系统管理员账号禁止编辑', 'danger')
        except Exception as e:
            current_app.logger.error(f"用户保存失败: {str(e)}", exc_info=True)
            flash('保存失败，请检查输入或联系管理员', 'danger')

    return render_template(
        'core/admin/system_user_edit.html',
        form=form,
        user=user,
        is_edit=is_edit
    )


@admin_bp.route('/system-user/toggle-active/<int:user_id>', methods=['POST'])
def toggle_active(user_id):
    """AJAX 或表单切换用户启用/禁用状态"""
    active = request.form.get('active') == 'true'

    try:
        UserService.toggle_user_active(user_id, active)
        status_text = "启用" if active else "禁用"
        flash(f'用户已{status_text}', 'success')
    except ValueError as ve:
        flash(str(ve), 'danger')
    except PermissionError:
        flash('系统管理员账号禁止更改状态', 'danger')
    except Exception as e:
        current_app.logger.error(f"用户状态切换失败: {str(e)}", exc_info=True)
        flash('操作失败，请稍后重试', 'danger')

    return redirect(url_for('admin.system_users'))


@admin_bp.route('/system-settings', methods=['GET', 'POST'])
def system_settings():
    """系统设置页面"""
    try:
        current_settings = SettingsService.get_all_settings()
    except Exception as e:
        current_app.logger.error(f"加载系统设置失败: {str(e)}", exc_info=True)
        flash('加载设置失败，请检查数据库或联系管理员', 'danger')
        current_settings = {}

    form = SystemSettingsForm(data=current_settings)

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # 合并 form.data 和 request.form，处理模板中额外的 HTML 输入框
                all_data = dict(form.data)
                for key in request.form:
                    if key not in all_data:
                        all_data[key] = request.form.get(key)
                
                updated_count = SettingsService.save_settings_bulk(all_data)
                flash(f'设置保存成功（共更新 {updated_count} 项）', 'success')
                return redirect(url_for('admin.system_settings'))
            except Exception as e:
                current_app.logger.error(f"设置保存失败: {str(e)}", exc_info=True)
                flash('保存失败，请检查输入格式或联系管理员', 'danger')
        else:
            flash('表单验证失败，请检查输入内容', 'danger')

    return render_template(
        'core/admin/system_settings.html',
        form=form,
        settings=current_settings,
        active_section='settings'
    )


@admin_bp.errorhandler(403)
@admin_bp.errorhandler(Forbidden)
def forbidden_error(e):
    flash('权限不足，无法访问该页面', 'danger')
    return redirect(url_for('workspace.dashboard'))


@admin_bp.route('/permissions', methods=['GET', 'POST'])
def permissions_edit():
    """角色权限编辑页面"""
    form = PermissionForm()
    role_name_form = RoleNameForm()
    
    # 获取系统权限（分组）
    system_permissions = PermissionService.get_system_permissions()
    # 获取Node权限（分组）
    node_permissions = PermissionService.get_node_permissions()
    
    # 构建扁平权限列表用于兼容性
    all_perms_list = []
    for data in system_permissions.values():
        all_perms_list.extend(data['permissions'])
    for data in node_permissions.values():
        all_perms_list.extend(data['permissions'])
    
    role_permissions = {}
    for role in [UserRole.ADMIN, UserRole.LEADER, UserRole.EMPLOYEE]:
        role_permissions[role] = PermissionService.get_role_permissions_from_db(role)

    role_labels = dict(UserRole.LABELS)
    custom_leader_name = SettingsService.get_setting('role_name_leader')
    custom_employee_name = SettingsService.get_setting('role_name_employee')
    if custom_leader_name:
        role_labels[UserRole.LEADER] = custom_leader_name
    if custom_employee_name:
        role_labels[UserRole.EMPLOYEE] = custom_employee_name

    if request.method == 'POST':
        saved = False
        errors = []

        if role_name_form.validate_on_submit():
            try:
                SettingsService.save_setting('role_name_leader', role_name_form.role_name_leader.data)
                SettingsService.save_setting('role_name_employee', role_name_form.role_name_employee.data)
                saved = True
            except Exception as e:
                current_app.logger.error(f"角色名称保存失败: {str(e)}", exc_info=True)
                errors.append('角色名称')
        else:
            if role_name_form.errors:
                errors.append('角色名称')

        try:
            for role in [UserRole.LEADER, UserRole.EMPLOYEE]:
                perms = request.form.getlist(f'permissions_{role}')
                PermissionService.save_role_permissions(role, perms)
            saved = True
        except Exception as e:
            current_app.logger.error(f"权限保存失败: {str(e)}", exc_info=True)
            errors.append('权限')

        if saved and not errors:
            flash('保存成功', 'success')
        elif errors:
            flash(f'部分保存失败: {", ".join(errors)}', 'warning')
        else:
            flash('保存失败，请稍后重试', 'danger')
        
        return redirect(url_for('admin.permissions_edit'))

    role_name_form.role_name_leader.data = custom_leader_name or UserRole.LABELS[UserRole.LEADER]
    role_name_form.role_name_employee.data = custom_employee_name or UserRole.LABELS[UserRole.EMPLOYEE]

    return render_template(
        'core/admin/system_permissions.html',
        form=form,
        role_name_form=role_name_form,
        system_permissions=system_permissions,
        node_permissions=node_permissions,
        all_permissions=all_perms_list,
        role_permissions=role_permissions,
        role_labels=role_labels,
        active_section='permissions'
    )
