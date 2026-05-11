"""
================================================================================
文件：__init__.py
路径：/home/edo/cimf-v2/core/forms/__init__.py
================================================================================

功能说明：
    核心应用表单模块，导出所有表单类

版本：
    - 1.0: 从 Flask WTForms 迁移为 Django Forms

导出：
    - LoginForm: 登录表单
    - UserCreateForm: 用户创建表单
    - UserEditForm: 用户编辑表单
    - UserSearchForm: 用户搜索表单
    - SystemSettingsForm: 系统设置表单
    - ProfileForm: 个人资料表单
    - PreferencesForm: 偏好设置表单
    - ChangePasswordForm: 修改密码表单
    - PermissionForm: 权限编辑表单
"""

from .admin_forms import PermissionForm, SystemSettingsForm, UserCreateForm, UserEditForm, UserSearchForm
from .auth_forms import LoginForm
from .settings_forms import ChangePasswordForm, PreferencesForm, ProfileForm

__all__ = [
    'ChangePasswordForm',
    'LoginForm',
    'PermissionForm',
    'PreferencesForm',
    'ProfileForm',
    'SystemSettingsForm',
    'UserCreateForm',
    'UserEditForm',
    'UserSearchForm',
]
