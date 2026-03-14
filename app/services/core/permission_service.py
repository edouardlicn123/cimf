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
    # 系统设置 - 细化为查看和修改
    ('system.settings.view', '系统设置 - 查看'),
    ('system.settings.modify', '系统设置 - 修改'),
    
    # 权限管理 - 细化为查看和修改
    ('permissions.view', '权限管理 - 查看'),
    ('permissions.modify', '权限管理 - 修改'),
    
    # 人员管理 - 细化为 CRUD
    ('user.create', '人员管理 - 创建'),
    ('user.read', '人员管理 - 查看'),
    ('user.update', '人员管理 - 修改'),
    ('user.delete', '人员管理 - 删除'),
]


# 角色默认权限（leader 和 employee 可编辑）
ROLE_DEFAULT_PERMISSIONS: Dict[str, List[str]] = {
    UserRole.ADMIN: ['*'],  # 全部权限
    UserRole.LEADER: ['system.settings.view', 'system.settings.modify', 'permissions.view', 'permissions.modify', 'user.create', 'user.read', 'user.update', 'user.delete'],
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
    def get_system_permissions() -> Dict[str, Dict]:
        """获取系统权限，按模块分组"""
        return {
            'system_settings': {
                'name': '系统设置',
                'icon': 'bi-gear',
                'permissions': [
                    ('system.settings.view', '系统设置 - 查看'),
                    ('system.settings.modify', '系统设置 - 修改'),
                ]
            },
            'permissions': {
                'name': '权限管理',
                'icon': 'bi-shield-lock',
                'permissions': [
                    ('permissions.view', '权限管理 - 查看'),
                    ('permissions.modify', '权限管理 - 修改'),
                ]
            },
            'user': {
                'name': '人员管理',
                'icon': 'bi-people',
                'permissions': [
                    ('user.create', '人员管理 - 创建'),
                    ('user.read', '人员管理 - 查看'),
                    ('user.update', '人员管理 - 修改'),
                    ('user.delete', '人员管理 - 删除'),
                ]
            },
        }

    @staticmethod
    def get_node_permissions() -> Dict[str, Dict]:
        """获取已启用Node的CRUD权限，按node分组"""
        from app.services.node.node_type_service import NodeTypeService
        
        node_permissions = {}
        active_node_types = NodeTypeService.get_all()
        
        for node_type in active_node_types:
            slug = node_type.slug
            name = node_type.name
            icon = node_type.icon or 'bi-folder'
            node_permissions[slug] = {
                'name': name,
                'icon': icon,
                'permissions': [
                    (f'node.{slug}.create', f'{name} - 创建'),
                    (f'node.{slug}.read', f'{name} - 查看'),
                    (f'node.{slug}.update', f'{name} - 编辑'),
                    (f'node.{slug}.delete', f'{name} - 删除'),
                ]
            }
        
        return node_permissions

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
