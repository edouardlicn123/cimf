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

import logging
from typing import Any

from django.db import transaction
from django.utils import timezone

from core.models import User
from core.services.base_service import BaseService
from core.services.mixins import error_response
from core.services.settings_service import SettingsService

logger = logging.getLogger(__name__)


class AuthService(BaseService):
    """
    认证服务层
    处理用户登录、登出、锁定等逻辑
    """

    model_class = User

    @classmethod
    def authenticate(cls, username: str, password: str) -> tuple[User | None, User | None]:
        """
        验证用户凭据

        返回：
            (authenticated_user, looked_up_user)
            - authenticated_user: 验证成功的用户，失败则为 None
            - looked_up_user: 查找到的用户对象（即使密码错误也返回），未找到则为 None
        """
        user = cls.get_first(username=username)
        if not user:
            return None, None

        if not user.check_password(password):
            return None, user

        return user, user

    @classmethod
    def login(cls, username: str, password: str) -> dict[str, Any]:
        """处理用户登录，复用 authenticate 进行凭据验证"""
        user, looked_up_user = cls.authenticate(username, password)

        if not user:
            if looked_up_user:
                max_failures = cls.get_login_max_failures()
                lock_minutes = cls.get_login_lock_minutes()
                looked_up_user.record_failed_attempt(max_failures, lock_minutes)
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
        with transaction.atomic():
            count = User.objects.filter(locked_until__isnull=False, locked_until__lte=timezone.now()).update(
                failed_login_attempts=0, locked_until=None
            )
        return count

    @staticmethod
    def get_login_max_failures() -> int:
        """获取登录失败最大次数"""
        value = SettingsService.get_setting("login_max_failures", 5)
        try:
            return int(value) if value else 5
        except (ValueError, TypeError) as e:
            logger.warning("login_max_failures 配置值无效: %r — %s", value, e)
            return 5

    @staticmethod
    def get_login_lock_minutes() -> int:
        """获取登录锁定时间（分钟）"""
        value = SettingsService.get_setting("login_lock_minutes", 30)
        try:
            return int(value) if value else 30
        except (ValueError, TypeError) as e:
            logger.warning("login_lock_minutes 配置值无效: %r — %s", value, e)
            return 30
