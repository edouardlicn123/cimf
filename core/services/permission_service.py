"""
================================================================================
文件：permission_service.py
路径：/home/edo/cimf-v2/core/services/permission_service.py
================================================================================

功能说明：
    权限服务层，定义权限列表、角色默认权限，提供权限检查、角色管理等核心逻辑

    主要功能：
    - 权限定义和列表
    - 角色权限管理
    - 权限检查
    - 访问控制

用法：
    1. 检查用户权限：
        if PermissionService.has_permission(user, 'system.settings.view'):
            pass

    2. 获取用户有效权限：
        perms = PermissionService.get_user_effective_permissions(user)

版本：
    - 1.0: 从 Flask 迁移

依赖：
    - core.models.User: 用户模型
    - core.models.SystemSetting: 系统设置模型
"""

import inspect
import json
import logging
import re

from django.urls import get_resolver

from core.constants import Perm, UserRole
from core.models import User
from core.module.models import Module

logger = logging.getLogger(__name__)

PERMISSION_GROUPS: list[dict] = [
    {
        "key": "system_settings",
        "name": "系统设置",
        "icon": "bi-gear",
        "permissions": [
            (Perm.SYSTEM_SETTINGS_VIEW, "系统设置 - 查看"),
            (Perm.SYSTEM_SETTINGS_MODIFY, "系统设置 - 修改"),
        ],
    },
    {
        "key": "permissions",
        "name": "权限管理",
        "icon": "bi-shield-lock",
        "permissions": [
            (Perm.PERMISSIONS_VIEW, "权限管理 - 查看"),
            (Perm.PERMISSIONS_MODIFY, "权限管理 - 修改"),
        ],
    },
    {
        "key": "user",
        "name": "人员管理",
        "icon": "bi-people",
        "permissions": [
            (Perm.USER_CREATE, "人员管理 - 创建"),
            (Perm.USER_READ, "人员管理 - 查看"),
            (Perm.USER_UPDATE, "人员管理 - 修改"),
            (Perm.USER_DELETE, "人员管理 - 删除"),
        ],
    },
    {
        "key": "importexport",
        "name": "数据导入导出",
        "icon": "bi-arrow-down-up",
        "permissions": [
            (Perm.IMPORTEXPORT_VIEW, "数据导入导出 - 访问"),
        ],
    },
]

PERMISSIONS: list[tuple[str, str]] = [
    perm for group in PERMISSION_GROUPS for perm in group["permissions"]
]

ROLE_DEFAULT_PERMISSIONS: dict[str, list[str]] = {
    UserRole.MANAGER: [Perm.IMPORTEXPORT_VIEW],
    UserRole.LEADER: [Perm.IMPORTEXPORT_VIEW],
    UserRole.EMPLOYEE: [],
}


class PermissionService:
    """
    权限服务层
    提供权限定义、角色管理、权限检查等功能
    """

    @staticmethod
    def get_all_permissions() -> list[tuple]:
        """获取所有可用权限列表"""
        return PERMISSIONS

    @staticmethod
    def get_system_permissions() -> dict[str, dict]:
        """获取系统权限，按模块分组"""
        return {
            group["key"]: {
                "name": group["name"],
                "icon": group["icon"],
                "permissions": group["permissions"][:],
            }
            for group in PERMISSION_GROUPS
        }

    @staticmethod
    def get_role_permissions(role: str) -> list[str]:
        """获取指定角色的默认权限"""
        return ROLE_DEFAULT_PERMISSIONS.get(role, [])

    @staticmethod
    def get_role_permissions_from_db(role: str) -> list[str]:
        """从数据库获取角色权限（优先）或使用默认值"""
        from core.services import SettingsService  # noqa: PLC0415

        setting_key = f"role_permissions_{role}"
        value = SettingsService.get_setting(setting_key, parse_json=True)

        if value is not None:
            return value

        return ROLE_DEFAULT_PERMISSIONS.get(role, [])

    @staticmethod
    def save_role_permissions(role: str, permissions: list[str]) -> None:
        """保存角色权限到数据库"""
        from core.services import SettingsService  # noqa: PLC0415

        setting_key = f"role_permissions_{role}"
        value = json.dumps(permissions)
        label = UserRole.LABELS.get(role, role)
        SettingsService.save_setting(setting_key, value, description=f"角色 [{label}] 的默认权限")

    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        """检查用户是否拥有指定权限"""
        if user.is_admin:
            return True

        perms = PermissionService.get_role_permissions_from_db(user.role)
        return permission in perms

    @staticmethod
    def get_user_effective_permissions(user: User) -> list[str]:
        """获取用户的有效权限列表（考虑角色）"""
        if user.is_admin:
            return ["*"]

        return PermissionService.get_role_permissions_from_db(user.role)

    @staticmethod
    def can_access_admin(user: User) -> bool:
        """检查用户是否可以访问后台"""
        return user.is_admin

    @staticmethod
    def init_default_role_permissions() -> None:
        """初始化角色默认权限到数据库（优化版：批量查询）"""
        from core.models import SystemSetting  # noqa: PLC0415

        existing_keys = set(
            SystemSetting.objects.filter(key__startswith="role_permissions_").values_list("key", flat=True)
        )

        for role, perms in ROLE_DEFAULT_PERMISSIONS.items():
            setting_key = f"role_permissions_{role}"
            if setting_key not in existing_keys:
                PermissionService.save_role_permissions(role, perms)

    @staticmethod
    def check_node_permission(user: User, node, permission_type: str) -> tuple[bool, str | None]:
        """检查用户对指定节点的操作权限"""
        if user.is_admin:
            return True, None

        if node.created_by_id == user.id:
            return True, None

        perm_map = {
            "view": f"node.{node.node_type.slug}.view_others",
            "edit": f"node.{node.node_type.slug}.edit_others",
            "delete": f"node.{node.node_type.slug}.delete_others",
        }
        perm = perm_map.get(permission_type)
        if perm and PermissionService.has_permission(user, perm):
            return True, None

        return False, f"您没有权限{permission_type}别人的客户信息"

    @staticmethod
    def get_node_permissions() -> dict[str, dict]:
        """获取节点权限，按节点类型分组（从模块配置动态读取）"""
        node_permissions = {}

        # 获取已安装且已启用的模块
        active_modules = Module.objects.filter(is_installed=True, is_active=True, module_type="node")

        for module in active_modules:
            # 基础权限（自动添加）
            perms = [
                (f"node.{module.module_id}.create", f"{module.name} - 创建"),
                (f"node.{module.module_id}.read", f"{module.name} - 查看"),
                (f"node.{module.module_id}.update", f"{module.name} - 修改"),
                (f"node.{module.module_id}.delete", f"{module.name} - 删除"),
            ]

            # 从 module.py 读取自定义权限
            from core.module.services.module_service import ModuleService  # noqa: PLC0415

            module_info = ModuleService.load_module_info(module.path)
            icon = module_info.get("icon", "bi-folder") if module_info else "bi-folder"
            if module_info:
                perms.extend(
                    (f"node.{module.module_id}.{perm['key']}", f"{module.name} - {perm['name']}")
                    for perm in module_info.get("permissions", [])
                )

            node_permissions[module.module_id] = {"name": module.name, "icon": icon, "permissions": perms}

        return node_permissions


def get_all_pages_with_permission_status():
    """获取所有页面的权限状态（URL 模式 + 是否含 admin 检查）"""
    pages = []
    visited_views = set()

    def extract_patterns(patterns):
        for pattern in patterns:
            if hasattr(pattern, "url_patterns"):
                extract_patterns(pattern.url_patterns)
            elif hasattr(pattern, "callback") and pattern.callback:
                view_func = pattern.callback
                view_name = getattr(view_func, "__name__", pattern.name or "unknown")
                url_pattern = str(pattern.pattern)
                url_pattern = url_pattern.lstrip("^").rstrip("$")

                if not url_pattern or url_pattern == "/":
                    continue

                admin_views = {
                    "changelist_view", "add_view", "change_view", "delete_view",
                    "history_view", "app_index", "autocomplete_view", "i18n_javascript",
                    "password_change", "password_change_done", "user_change_password",
                    "catch_all_view", "view", "shortcut", "login", "logout", "index", "jsi18n",
                }
                if view_name in admin_views and not pattern.name:
                    continue

                if re.match(r"^\w+/", url_pattern) and not pattern.name:
                    continue

                if url_pattern.endswith(("/add/", "/delete/")):
                    continue

                if view_func in visited_views:
                    continue
                visited_views.add(view_func)

                has_admin_check = "PermissionService.can_access_admin" in (
                    inspect.getsource(view_func) if callable(view_func) else ""
                )

                pages.append({
                    "name": pattern.name or view_name,
                    "url": url_pattern,
                    "has_admin_check": has_admin_check,
                })

    try:
        extract_patterns(get_resolver().url_patterns)
    except Exception as e:
        logger.warning(f"提取URL模式失败: {e}", exc_info=True)

    return pages
