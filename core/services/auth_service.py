"""
================================================================================
文件：auth_service.py
路径：/home/edo/cimf-v2/core/services/auth_service.py
================================================================================

功能说明：
    认证服务层，处理用户登录、登出、锁定等逻辑

    主要功能：
    - 用户登录验证
    - 登录失败处理
    - 账号锁定检测
    - 会话管理

用法：
    1. 登录验证：
        result = AuthService.login(username, password)
        if result['success']:
            login(request, user)

    2. 检查账号锁定：
        if AuthService.is_account_locked(user):
            pass

版本：
    - 1.0: 从 Flask 迁移

依赖：
    - core.models.User: 用户模型
    - core.services.settings_service: 设置服务
"""

from typing import Any

from django.utils import timezone

from core.models import User
from core.services.base_service import BaseService
from core.services.mixins import error_response
from core.services.settings_service import SettingsService


class AuthService(BaseService):
    """
    认证服务层
    处理用户登录、登出、锁定等逻辑
    """

    model_class = User

    @classmethod
    def authenticate(cls, username: str, password: str) -> User | None:
        """
        验证用户凭据

        参数：
            username: 用户名
            password: 密码

        返回：
            用户对象（验证成功）或 None（验证失败）
        """
        user = cls.get_first(username=username)
        if not user:
            return None

        if not user.check_password(password):
            return None

        return user

    @classmethod
    def login(cls, _request, username: str, password: str) -> dict[str, Any]:
        """
        处理用户登录

        参数：
            request: HTTP 请求对象
            username: 用户名
            password: 密码

        返回：
            包含 success、message、user 的字典
        """
        user = cls.authenticate(username, password)

        if not user:
            return error_response("用户名或密码错误", user=None)

        if user.is_locked():
            return error_response(
                f"账号已被锁定，请于 {user.locked_until.strftime('%H:%M')} 后再试",
                user=None,
            )

        if not user.is_active:
            return error_response("账号已被禁用", user=None)

        user.record_login()
        return {"success": True, "message": "登录成功", "user": user}

    @staticmethod
    def is_account_locked(user: User) -> bool:
        """检查账号是否被锁定"""
        return user.is_locked()

    @staticmethod
    def unlock_expired_accounts() -> int:
        """解锁过期的锁定账号"""
        expired_users = User.objects.filter(locked_until__isnull=False, locked_until__lte=timezone.now())
        count = expired_users.count()

        for user in expired_users:
            user.failed_login_attempts = 0
            user.locked_until = None
            user.save()

        return count

    @staticmethod
    def get_login_max_failures() -> int:
        """获取登录失败最大次数"""
        value = SettingsService.get_setting("login_max_failures", 5)
        try:
            return int(value) if value else 5
        except (ValueError, TypeError):
            return 5

    @staticmethod
    def get_login_lock_minutes() -> int:
        """获取登录锁定时间（分钟）"""
        value = SettingsService.get_setting("login_lock_minutes", 30)
        try:
            return int(value) if value else 30
        except (ValueError, TypeError):
            return 30
