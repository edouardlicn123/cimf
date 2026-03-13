# 文件路径：app/routes/main.py
# 更新日期：2026-02-17
# 功能说明：主蓝图路由集合，负责仪表盘、个人中心、关于、帮助、设置等非管理类页面；严格遵守路由层薄原则，所有业务逻辑（如统计、用户更新）应逐步迁移到 service 层（当前版本部分仍直接操作模型，待重构）

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user, logout_user
from datetime import datetime
from app import db
from app.forms.settings_forms import ProfileForm, PreferencesForm, ChangePasswordForm  # 假设表单已移到 forms/settings_forms.py

main_bp = Blueprint('main', __name__)


@main_bp.before_request
@login_required
def require_login():
    """所有主蓝图路由默认要求登录（统一保护）"""
    pass


@main_bp.route('/', methods=['GET'])
@main_bp.route('/index', methods=['GET'])
@main_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """
    系统仪表盘首页（已登录用户默认入口）
    当前统计数据为占位，后续应调用 UserService 或 ProjectService 获取真实数据
    """
    # 占位统计数据（后续替换为 service 调用）
    stats = {
        'project_count': 0,              # 项目总数
        'active_projects': 0,            # 进行中项目
        'pending_tasks': 0,              # 待办事项
        'unread_notifications': 0,       # 未读通知
        'total_volume_m3': 0.0,          # 累计体积（m³）
        'total_freight_usd': 0.0,        # 累计运费（USD）
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
            '欢迎首次登录！建议前往“设置”完善昵称、邮箱和偏好。',
            'info'
        )

    return render_template('main/dashboard.html', **context)


@main_bp.route('/profile', methods=['GET'])
def profile():
    """个人中心 - 查看个人信息（只读视图）"""
    return render_template(
        'main/profile.html',
        title='个人中心',
        user=current_user
    )


@main_bp.route('/about', methods=['GET'])
def about():
    """关于系统页面"""
    return render_template(
        'main/about.html',
        title='关于系统'
    )


@main_bp.route('/help', methods=['GET'])
def help_page():
    """帮助中心页面"""
    return render_template(
        'main/help.html',
        title='帮助中心'
    )


@main_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """用户设置页面：个人信息 + 偏好设置 + 修改密码（多表单共存）"""
    profile_form = ProfileForm(obj=current_user)
    pref_form = PreferencesForm(obj=current_user)
    pwd_form = ChangePasswordForm()

    if request.method == 'POST':
        form_submitted = False

        # 个人信息表单提交
        if 'submit_profile' in request.form and profile_form.validate_on_submit():
            current_user.nickname = profile_form.nickname.data.strip() or None
            current_user.email = profile_form.email.data.strip() or None
            db.session.commit()
            flash('个人信息已更新成功', 'success')
            form_submitted = True

        # 偏好设置表单提交
        elif 'submit_preferences' in request.form and pref_form.validate_on_submit():
            current_user.theme = pref_form.theme.data
            current_user.notifications_enabled = pref_form.notifications.data
            current_user.preferred_language = pref_form.language.data
            db.session.commit()
            flash('偏好设置已保存', 'success')
            form_submitted = True

        # 修改密码表单提交
        elif 'submit_password' in request.form and pwd_form.validate_on_submit():
            if current_user.check_password(pwd_form.old_password.data):
                current_user.set_password(pwd_form.new_password.data)
                current_user.last_login_at = datetime.utcnow()  # 可选：记录修改时间
                current_user.reset_failed_attempts()  # 清零失败次数（如果模型有此方法）
                db.session.commit()
                flash('密码修改成功，请使用新密码重新登录', 'success')
                logout_user()
                return redirect(url_for('auth.login'))
            else:
                flash('原密码错误，请重试', 'danger')

        if not form_submitted:
            flash('表单验证失败，请检查输入内容', 'danger')

    return render_template(
        'main/settings.html',
        title='设置',
        profile_form=profile_form,
        pref_form=pref_form,
        pwd_form=pwd_form,
        user=current_user
    )
