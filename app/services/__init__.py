# 文件路径：app/services/__init__.py
# 功能说明：服务层导出（从 core 重新导出）

from app.services.core import (
    login_attempt, 
    get_post_login_redirect, 
    safe_logout,
    UserService, 
    SettingsService,
    PermissionService,
    UserRole,
    shipping,
    volume_kd,
    SERVICES
)

__all__ = [
    'login_attempt', 
    'get_post_login_redirect', 
    'safe_logout',
    'UserService', 
    'SettingsService',
    'PermissionService',
    'UserRole',
    'shipping',
    'volume_kd',
    'SERVICES'
]
