# app/modules/core/auth/routes.py
# 功能说明：认证模块路由集合，负责登录、登出等认证相关页面

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required, login_user, logout_user
from app.forms.auth_forms import LoginForm
from app.services import login_attempt, get_post_login_redirect, safe_logout
from app import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('您已登录，无需重复登录', 'info')
        return redirect(url_for('workspace.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        remember = form.remember_me.data

        success, error_msg, user = login_attempt(username, password, remember)

        if success:
            user.reset_failed_attempts()
            user.record_login()
            db.session.commit()

            flash('登录成功，欢迎回来！', 'success')
            return redirect(get_post_login_redirect())

        else:
            if user and user.is_locked():
                flash(f'账号已被锁定，请 {user.locked_until.strftime("%Y-%m-%d %H:%M")} 后再试', 'danger')
            elif user:
                pass
            else:
                flash('用户名或密码错误', 'danger')

    next_url = request.args.get('next')
    if next_url and (next_url.startswith('/') and not next_url.startswith('//')):
        flash(f'请先登录以访问 {next_url}', 'info')
    else:
        next_url = None

    return render_template(
        'core/auth/login.html',
        form=form,
        title='登录 - FFE 项目跟进系统',
        next=next_url
    )


@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    safe_logout()
    flash('您已安全退出登录', 'info')

    next_url = request.args.get('next')
    if next_url and next_url.startswith('/') and not next_url.startswith('//'):
        return redirect(next_url)

    return redirect(url_for('auth.login'))
