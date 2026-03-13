# app/modules/profile/routes.py
# 功能说明：个人中心模块路由集合

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user, logout_user
from datetime import datetime
from app import db
from app.forms.settings_forms import ProfileForm, PreferencesForm, ChangePasswordForm

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.before_request
@login_required
def require_login():
    """所有个人中心路由默认要求登录"""
    pass


@profile_bp.route('/', methods=['GET'])
@profile_bp.route('/view', methods=['GET'])
def view():
    """个人中心 - 查看个人信息"""
    return render_template(
        'core/main/profile.html',
        title='个人中心',
        user=current_user
    )


@profile_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """用户设置页面"""
    profile_form = ProfileForm(obj=current_user)
    pref_form = PreferencesForm(obj=current_user)
    pwd_form = ChangePasswordForm()

    if request.method == 'POST':
        form_submitted = False

        if 'submit_profile' in request.form and profile_form.validate_on_submit():
            current_user.nickname = profile_form.nickname.data.strip() if profile_form.nickname.data else None
            current_user.email = profile_form.email.data.strip() if profile_form.email.data else None
            db.session.commit()
            flash('个人信息已更新成功', 'success')
            form_submitted = True

        elif 'submit_preferences' in request.form and pref_form.validate_on_submit():
            current_user.theme = pref_form.theme.data
            current_user.notifications_enabled = pref_form.notifications.data
            current_user.preferred_language = pref_form.language.data
            db.session.commit()
            flash('偏好设置已保存', 'success')
            form_submitted = True

        elif 'submit_password' in request.form and pwd_form.validate_on_submit():
            if current_user.check_password(pwd_form.current_password.data):
                current_user.set_password(pwd_form.new_password.data)
                current_user.last_login_at = datetime.utcnow()
                current_user.reset_failed_attempts()
                db.session.commit()
                flash('密码修改成功，请使用新密码重新登录', 'success')
                logout_user()
                return redirect(url_for('auth.login'))
            else:
                flash('原密码错误，请重试', 'danger')

        if not form_submitted:
            flash('表单验证失败，请检查输入内容', 'danger')

    return render_template(
        'core/main/settings.html',
        title='设置',
        profile_form=profile_form,
        pref_form=pref_form,
        pwd_form=pwd_form,
        user=current_user
    )
