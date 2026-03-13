# 文件路径：app/services/auth_service.py
# 更新日期：2026-02-17
# 功能说明：认证相关核心业务逻辑，包括登录尝试、密码验证、登录后重定向逻辑、安全登出处理等，所有数据库操作封装在此层，路由层不应直接访问 User 模型

from flask import current_app, request, url_for
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from datetime import datetime


def login_attempt(username: str, password: str, remember: bool = False) -> tuple[bool, str | None, User | None]:
    """
    尝试用户登录，返回三元组：
    - success: bool - 是否登录成功
    - error_msg: str or None - 错误消息（成功时为 None）
    - user: User or None - 成功登录的用户对象（失败时为 None）
    
    包含登录失败计数、账号锁定检查、重置失败次数等安全机制
    """
    username = username.strip()
    user = User.query.filter_by(username=username).first()

    if not user:
        return False, "用户名不存在", None

    # 检查是否锁定
    if user.is_locked():
        return False, "账号已被锁定，请稍后再试", None

    # 验证密码
    if not user.check_password(password):
        user.record_failed_attempt()
        db.session.commit()
        if user.is_locked():
            return False, "密码错误次数过多，账号已临时锁定", None
        return False, "密码错误", None

    # 检查账号是否启用
    if not user.is_active:
        return False, "账号已被禁用，请联系管理员", None

    # 登录成功
    user.reset_failed_attempts()
    user.record_login()
    db.session.commit()

    # 执行登录（设置 session）
    login_user(user, remember=remember)

    current_app.logger.info(f"用户登录成功: {username} (ID: {user.id})")
    return True, None, user


def get_post_login_redirect() -> str:
    """
    获取登录成功后的重定向地址
    优先级：next 参数 → 仪表盘 → 首页
    """
    next_page = request.args.get('next')
    if next_page and next_page.startswith('/'):
        return next_page
    return url_for('workspace.dashboard')


def safe_logout() -> None:
    """
    安全登出：记录日志、清除 session、清空 remember cookie
    
    注意：此函数必须在请求上下文中调用（路由层），因为 logout_user() 依赖 session 和 current_user
    """
    if current_user.is_authenticated:
        current_app.logger.info(f"用户登出: {current_user.username} (ID: {current_user.id})")
        logout_user()
        # 可选：额外清理 session 或 token（如果有）
    else:
        current_app.logger.debug("尝试登出时未检测到已登录用户")


def record_login_success(user: User) -> None:
    """
    记录成功登录（备用函数，已在 login_attempt 中调用）
    """
    user.reset_failed_attempts()
    user.record_login()
    db.session.commit()


def record_login_failure(user: User | None = None) -> None:
    """
    记录登录失败（备用函数，已在 login_attempt 中处理）
    """
    if user:
        user.record_failed_attempt()
        db.session.commit()
