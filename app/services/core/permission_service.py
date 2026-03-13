# 文件路径：app/services/permission_service.py
# 更新日期：2026-03-10
# 功能说明：权限服务层，定义权限列表、角色默认权限，提供权限检查、角色管理等核心逻辑

from typing import Dict, List, Optional
from flask import current_app
from app import db
from app.models import User, SystemSetting


class UserRole:
    """角色常量"""
    ADMIN = 'admin'
    LEADER = 'leader'
    EMPLOYEE = 'employee'

    CHOICES = [
        (ADMIN, '管理员'),
        (LEADER, '组长'),
        (EMPLOYEE, '普通员工'),
    ]

    LABELS = {
        ADMIN: '管理员',
        LEADER: '组长',
        EMPLOYEE: '普通员工',
    }


# 可用权限列表（可扩展）
PERMISSIONS = [
    ('system.settings', '修改系统基本设置'),
    ('user.manage', '人员管理（新增及删改）'),
    ('permissions.manage', '权限管理'),
    # 未来可扩展：
    # ('project.view', '项目 - 查看'),
    # ('project.create', '项目 - 创建'),
    # ('project.edit', '项目 - 编辑'),
    # ('project.delete', '项目 - 删除'),
    # ('report.export', '报表 - 导出'),
]


# 角色默认权限（leader 和 employee 可编辑）
ROLE_DEFAULT_PERMISSIONS: Dict[str, List[str]] = {
    UserRole.ADMIN: ['*'],  # 全部权限
    UserRole.LEADER: ['system.settings', 'user.manage', 'permissions.manage'],
    UserRole.EMPLOYEE: [],
}


class PermissionService:
    """
    权限服务层
    提供权限定义、角色管理、权限检查等功能
    """

    @staticmethod
    def get_all_permissions() -> List[tuple]:
        """获取所有可用权限列表"""
        return PERMISSIONS

    @staticmethod
    def get_role_permissions(role: str) -> List[str]:
        """获取指定角色的默认权限"""
        return ROLE_DEFAULT_PERMISSIONS.get(role, [])

    @staticmethod
    def get_role_permissions_from_db(role: str) -> List[str]:
        """从数据库获取角色权限（优先）或使用默认值"""
        setting_key = f'role_permissions_{role}'
        setting = SystemSetting.query.filter_by(key=setting_key).first()
        
        if setting and setting.value:
            import json
            try:
                return json.loads(setting.value)
            except (json.JSONDecodeError, TypeError):
                pass
        
        return ROLE_DEFAULT_PERMISSIONS.get(role, [])

    @staticmethod
    def save_role_permissions(role: str, permissions: List[str]) -> None:
        """保存角色权限到数据库"""
        setting_key = f'role_permissions_{role}'
        import json
        value = json.dumps(permissions)
        
        setting = SystemSetting.query.filter_by(key=setting_key).first()
        if setting:
            setting.value = value
        else:
            setting = SystemSetting(
                key=setting_key,
                value=value,
                description=f'角色 [{UserRole.LABELS.get(role, role)}] 的默认权限'
            )
            db.session.add(setting)
        
        db.session.commit()
        current_app.logger.info(f"角色权限已更新: {role} -> {permissions}")

    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        """检查用户是否拥有指定权限"""
        if user.role == UserRole.ADMIN:
            return True
        
        if user.role == UserRole.LEADER:
            leader_perms = PermissionService.get_role_permissions_from_db(UserRole.LEADER)
            return permission in leader_perms
        
        if user.role == UserRole.EMPLOYEE:
            emp_perms = PermissionService.get_role_permissions_from_db(UserRole.EMPLOYEE)
            return permission in emp_perms
        
        return False

    @staticmethod
    def get_user_effective_permissions(user: User) -> List[str]:
        """获取用户的有效权限列表（考虑角色）"""
        if user.role == UserRole.ADMIN:
            return ['*']
        
        return PermissionService.get_role_permissions_from_db(user.role)

    @staticmethod
    def can_access_admin(user: User) -> bool:
        """检查用户是否可以访问后台"""
        return user.role in [UserRole.ADMIN, UserRole.LEADER]

    @staticmethod
    def init_default_role_permissions() -> None:
        """初始化角色默认权限到数据库（仅当数据库中不存在时）"""
        for role, perms in ROLE_DEFAULT_PERMISSIONS.items():
            setting_key = f'role_permissions_{role}'
            if not SystemSetting.query.filter_by(key=setting_key).first():
                PermissionService.save_role_permissions(role, perms)
