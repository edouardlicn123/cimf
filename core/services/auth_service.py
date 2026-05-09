# -*- coding: utf-8 -*-
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

from typing import Optional, Dict, Any
from django.contrib.auth import authenticate
from django.utils import timezone
from core.models import User
from core.services.settings_service import SettingsService


class AuthService:
    """
    认证服务层
    处理用户登录、登出、锁定等逻辑
    """
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """
        验证用户凭据
        
        参数：
            username: 用户名
            password: 密码
            
        返回：
            用户对象（验证成功）或 None（验证失败）
        """
        user = User.objects.filter(username=username).first()
        if not user:
            return None
        
        if not user.check_password(password):
            return None
        
        return user
    
    @staticmethod
    def login(request, username: str, password: str) -> Dict[str, Any]:
        """
        处理用户登录
        
        参数：
            request: HTTP 请求对象
            username: 用户名
            password: 密码
            
        返回：
            包含 success、message、user 的字典
        """
        user = User.objects.filter(username=username).first()
        
        if not user:
            return {
                'success': False,
                'message': '用户名或密码错误',
                'user': None
            }
        
        if user.is_locked():
            return {
                'success': False,
                'message': f'账号已被锁定，请于 {user.locked_until.strftime("%H:%M")} 后再试',
                'user': None
            }
        
        if not user.is_active:
            return {
                'success': False,
                'message': '账号已被禁用',
                'user': None
            }
        
        if not user.check_password(password):
            user.record_failed_attempt()
            return {
                'success': False,
                'message': '用户名或密码错误',
                'user': None
            }
        
        user.record_login()
        return {
            'success': True,
            'message': '登录成功',
            'user': user
        }
    
    @staticmethod
    def is_account_locked(user: User) -> bool:
        """检查账号是否被锁定"""
        return user.is_locked()
    
    @staticmethod
    def unlock_expired_accounts() -> int:
        """解锁过期的锁定账号"""
        expired_users = User.objects.filter(
            locked_until__isnull=False,
            locked_until__lte=timezone.now()
        )
        count = expired_users.count()
        
        for user in expired_users:
            user.failed_login_attempts = 0
            user.locked_until = None
            user.save()
        
        return count
    
    @staticmethod
    def get_login_max_failures() -> int:
        """获取登录失败最大次数"""
        value = SettingsService.get_setting('login_max_failures', 5)
        try:
            return int(value) if value else 5
        except (ValueError, TypeError):
            return 5
    
    @staticmethod
    def get_login_lock_minutes() -> int:
        """获取登录锁定时间（分钟）"""
        value = SettingsService.get_setting('login_lock_minutes', 30)
        try:
            return int(value) if value else 30
        except (ValueError, TypeError):
            return 30
