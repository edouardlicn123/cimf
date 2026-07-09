"""
===============================================================================
文件：__init__.py
路径：/home/edo/cimf-v2/core/forms/__init__.py
===============================================================================

功能说明：
    核心应用表单模块，导出所有表单类

版本：
    - 1.0: 从 Flask WTForms 迁移为 Django Forms

Bootstrap 样式约定：
    使用 BootstrapFormMixin（位于 mixins.py）自动为字段添加 Bootstrap class。
    该 Mixin 会跳过已手动指定 class 的字段（widget.attrs 含 "class" 键）。

    当前使用 Mixin 的表单：
    - UserCreateForm (admin_forms.py)
    - UserEditForm   (admin_forms.py)

    手工设置 widget.attrs["class"] 的表单（未使用 Mixin）：
    - LoginForm          (auth_forms.py)
    - ProfileForm        (settings_forms.py)
    - PreferencesForm    (settings_forms.py)
    - ChangePasswordForm (settings_forms.py)
    - UserSearchForm     (admin_forms.py)
    - SystemSettingsForm (admin_forms.py)

    如需为某表单启用 Mixin，继承 BootstrapFormMixin 并移除手工 class 即可。

导出：
    - LoginForm: 登录表单
    - UserCreateForm: 用户创建表单
    - UserEditForm: 用户编辑表单
    - UserSearchForm: 用户搜索表单
    - SystemSettingsForm: 系统设置表单
    - ProfileForm: 个人资料表单
    - PreferencesForm: 偏好设置表单
    - ChangePasswordForm: 修改密码表单
"""

from .admin_forms import SystemSettingsForm, UserCreateForm, UserEditForm, UserSearchForm
from .auth_forms import LoginForm
from .settings_forms import ChangePasswordForm, PreferencesForm, ProfileForm

__all__ = [
    "ChangePasswordForm",
    "LoginForm",
    "PreferencesForm",
    "ProfileForm",
    "SystemSettingsForm",
    "UserCreateForm",
    "UserEditForm",
    "UserSearchForm",
]
