# -*- coding: utf-8 -*-
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

import json
from typing import Dict, List, Optional
from core.models import User
from core.constants import UserRole


PERMISSIONS = [
    ('system.settings.view', '系统设置 - 查看'),
    ('system.settings.modify', '系统设置 - 修改'),
    ('permissions.view', '权限管理 - 查看'),
    ('permissions.modify', '权限管理 - 修改'),
    ('user.create', '人员管理 - 创建'),
    ('user.read', '人员管理 - 查看'),
    ('user.update', '人员管理 - 修改'),
    ('user.delete', '人员管理 - 删除'),
    ('importexport.view', '数据导入导出 - 访问'),
]


ROLE_DEFAULT_PERMISSIONS: Dict[str, List[str]] = {
    UserRole.MANAGER: ['importexport.view'],
    UserRole.LEADER: ['importexport.view'],
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
            'importexport': {
                'name': '数据导入导出',
                'icon': 'bi-arrow-down-up',
                'permissions': [
                    ('importexport.view', '数据导入导出 - 访问'),
                ]
            },
        }
    
    @staticmethod
    def get_role_permissions(role: str) -> List[str]:
        """获取指定角色的默认权限"""
        return ROLE_DEFAULT_PERMISSIONS.get(role, [])
    
    @staticmethod
    def get_role_permissions_from_db(role: str) -> List[str]:
        """从数据库获取角色权限（优先）或使用默认值"""
        from core.models import SystemSetting
        
        setting_key = f'role_permissions_{role}'
        setting = SystemSetting.objects.filter(key=setting_key).first()
        
        if setting and setting.value:
            try:
                return json.loads(setting.value)
            except (json.JSONDecodeError, TypeError):
                pass
        
        return ROLE_DEFAULT_PERMISSIONS.get(role, [])
    
    @staticmethod
    def save_role_permissions(role: str, permissions: List[str]) -> None:
        """保存角色权限到数据库"""
        from core.models import SystemSetting
        
        setting_key = f'role_permissions_{role}'
        value = json.dumps(permissions)
        
        SystemSetting.objects.update_or_create(
            key=setting_key,
            defaults={
                'value': value,
                'description': f'角色 [{UserRole.LABELS.get(role, role)}] 的默认权限'
            }
        )
    
    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        """检查用户是否拥有指定权限"""
        if user.is_admin:
            return True
        
        if user.role == UserRole.MANAGER:
            manager_perms = PermissionService.get_role_permissions_from_db(UserRole.MANAGER)
            return permission in manager_perms
        
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
        if user.is_admin:
            return ['*']
        
        return PermissionService.get_role_permissions_from_db(user.role)
    
    @staticmethod
    def can_access_admin(user: User) -> bool:
        """检查用户是否可以访问后台"""
        return user.is_admin == True
    
    @staticmethod
    def init_default_role_permissions() -> None:
        """初始化角色默认权限到数据库（优化版：批量查询）"""
        from core.models import SystemSetting
        
        existing_keys = set(SystemSetting.objects.filter(
            key__startswith='role_permissions_'
        ).values_list('key', flat=True))
        
        for role, perms in ROLE_DEFAULT_PERMISSIONS.items():
            setting_key = f'role_permissions_{role}'
            if setting_key not in existing_keys:
                PermissionService.save_role_permissions(role, perms)
    
    @staticmethod
    def get_node_permissions() -> Dict[str, Dict]:
        """获取节点权限，按节点类型分组（从模块配置动态读取）"""
        from core.module.models import Module
        from importlib import import_module
        
        node_permissions = {}
        
        # 获取已安装且已启用的模块
        active_modules = Module.objects.filter(
            is_installed=True,
            is_active=True,
            module_type='node'
        )
        
        for module in active_modules:
            # 基础权限（自动添加）
            perms = [
                (f'node.{module.module_id}.create', f'{module.name} - 创建'),
                (f'node.{module.module_id}.read', f'{module.name} - 查看'),
                (f'node.{module.module_id}.update', f'{module.name} - 修改'),
                (f'node.{module.module_id}.delete', f'{module.name} - 删除'),
            ]
            
            # 从 module.py 读取自定义权限
            icon = 'bi-folder'
            try:
                mod = import_module(f'modules.{module.path}.module')
                if hasattr(mod, 'MODULE_INFO'):
                    module_info = mod.MODULE_INFO
                    icon = module_info.get('icon', 'bi-folder')
                    
                    # 添加模块自定义权限
                    for perm in module_info.get('permissions', []):
                        perms.append((
                            f'node.{module.module_id}.{perm["key"]}',
                            f'{module.name} - {perm["name"]}'
                        ))
            except (ImportError, ModuleNotFoundError, AttributeError):
                pass
            
            node_permissions[module.module_id] = {
                'name': module.name,
                'icon': icon,
                'permissions': perms
            }
        
        return node_permissions
