# 文件路径：app/routes/auth.py
# 更新日期：2026-02-17
# 功能说明：认证模块路由集合，负责登录、登出等认证相关页面，只调用服务层进行核心逻辑，不直接操作数据库或模型

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required, login_user, logout_user
from app.forms.auth_forms import LoginForm  # 假设已移到 forms/auth_forms.py
from app.services.auth_service import login_attempt, get_post_login_redirect, safe_logout
from app import db  # 用于 commit（如果服务层未 commit）

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    登录路由
    
    特性：
    - 已登录用户自动跳转仪表盘，防止重复登录
    - 支持 ?next= 参数（登录成功后跳转原目标页，安全校验防止开放重定向）
    - 登录失败/锁定逻辑由 login_attempt() 处理
    - 失败次数与锁定状态直接从 User 模型读取
    """
    if current_user.is_authenticated:
        flash('您已登录，无需重复登录', 'info')
        return redirect(url_for('main.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        remember = form.remember_me.data

        # 调用服务层尝试登录
        success, error_msg, user = login_attempt(username, password, remember)

        if success:
            # 登录成功：重置失败计数、记录登录时间、登录用户
            user.reset_failed_attempts()
            user.record_login()
            db.session.commit()  # 确保计数和时间更新持久化

            flash('登录成功，欢迎回来！', 'success')
            return redirect(get_post_login_redirect())

        else:
            # 失败处理（服务层已 flash，这里补充锁定特判）
            if user and user.is_locked():
                flash(f'账号已被锁定，请 {user.locked_until.strftime("%Y-%m-%d %H:%M")} 后再试', 'danger')
            elif user:
                # 普通密码错误，已在 login_attempt 中记录失败次数
                pass  # flash 由服务层处理
            else:
                flash('用户名或密码错误', 'danger')

    # GET 或 验证失败时渲染
    next_url = request.args.get('next')
    # 安全校验：只允许内部相对路径
    if next_url and (next_url.startswith('/') and not next_url.startswith('//')):
        flash(f'请先登录以访问 {next_url}', 'info')
    else:
        next_url = None

    return render_template(
        'auth/login.html',
        form=form,
        title='登录 - FFE 项目跟进系统',
        next=next_url
    )


@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    """
    登出路由
    
    - 清除会话
    - flash 提示
    - 登出后统一跳转登录页（或支持 ?next= 参数跳转指定内部页面）
    """
    safe_logout()  # 只调用登出逻辑，不传参数
    flash('您已安全退出登录', 'info')

    # 可选：支持 ?next= 参数（登出后跳转指定内部页面，否则回登录页）
    next_url = request.args.get('next')
    if next_url and next_url.startswith('/') and not next_url.startswith('//'):
        return redirect(next_url)

    return redirect(url_for('auth.login'))


# ──────────────────────────────────────────────
# 未来扩展路由（按需启用，示例模板保留）
# ──────────────────────────────────────────────

# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     # TODO: 实现注册表单 + 邮箱验证（可选）
#     pass

# @auth_bp.route('/forgot-password', methods=['GET', 'POST'])
# def forgot_password():
#     # TODO: 发送重置密码邮件 + 生成 token
#     pass

# @auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     # TODO: 验证 token + 修改密码
#     pass

# @auth_bp.route('/change-password', methods=['GET', 'POST'])
# @login_required
# def change_password():
#     # TODO: 旧密码验证 + 新密码更新，成功后可选自动登出
#     pass
