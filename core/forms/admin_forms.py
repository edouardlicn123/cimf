"""
================================================================================
文件：admin_forms.py
路径：/home/edo/cimf-v2/core/forms/admin_forms.py
================================================================================

功能说明：
    后台管理相关 Django 表单定义，包括用户搜索、用户新建/编辑、
    系统设置、权限编辑表单

版本：
    - 1.0: 从 Flask WTForms 迁移为 Django Forms

依赖：
    - django.forms: Django 表单
    - core.models: 用户模型
    - core.services: 权限服务
"""

from django import forms
from django.core.exceptions import ValidationError

from core.constants import UserRole
from core.forms.mixins import (
    _USER_FORM_WIDGETS,
    BootstrapFormMixin,
    EmailCleanMixin,
    UsernameCleanMixin,
)
from core.forms.validators import (
    validate_password_confirmation,
    validate_unique_username,
)
from core.models import User


class UserSearchForm(BootstrapFormMixin, forms.Form):
    """用户搜索表单"""

    username = forms.CharField(
        label="用户名 / 昵称",
        max_length=64,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "输入用户名或昵称搜索（支持模糊匹配）",
            }
        ),
    )

    is_active = forms.BooleanField(
        label="仅显示启用用户",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={
                "role": "switch",
            }
        ),
    )


class UserCreateForm(BootstrapFormMixin, EmailCleanMixin, UsernameCleanMixin, forms.ModelForm):
    """用户创建表单"""

    password = forms.CharField(
        label="密码",
        min_length=10,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "用于登录的唯一账号（10+ 字符）",
                "autocomplete": "new-password",
            }
        ),
    )

    confirm_password = forms.CharField(
        label="确认密码",
        min_length=10,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "请再次输入密码以确认",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "nickname", "email", "role", "is_admin"]
        widgets = _USER_FORM_WIDGETS.copy()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].choices = UserRole.CHOICES
        self.fields["role"].initial = UserRole.EMPLOYEE

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password:
            validate_password_confirmation(password, confirm_password)
        return cleaned_data


class UserEditForm(BootstrapFormMixin, EmailCleanMixin, UsernameCleanMixin, forms.ModelForm):
    """用户编辑表单"""

    password = forms.CharField(
        label="新密码",
        required=False,
        min_length=10,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "编辑时留空则不修改密码",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "nickname", "email", "role", "is_admin", "is_active"]
        widgets = {
            **_USER_FORM_WIDGETS,
            "username": forms.TextInput(
                attrs={
                    "placeholder": "用于登录的唯一账号（3-64 字符）",
                    "autocomplete": "username",
                    "readonly": True,
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "role": "switch",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop("user_id", None)
        super().__init__(*args, **kwargs)
        self.fields["role"].choices = UserRole.CHOICES
        if self.instance and self.instance.pk:
            self._original_username = self.instance.username
        else:
            self._original_username = None

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            username = username.strip()
            if self._original_username and username != self._original_username:
                raise ValidationError("用户名不可修改")
            validate_unique_username(username, exclude_user_id=self.user_id)
        return username


class SystemSettingsForm(BootstrapFormMixin, forms.Form):
    """系统设置表单"""

    system_name = forms.CharField(
        label="系统名称",
        max_length=60,
        widget=forms.TextInput(
            attrs={
                "placeholder": "显示在导航栏和页面标题",
            }
        ),
    )

    upload_max_size_mb = forms.IntegerField(
        label="单个文件最大上传大小 (MB)",
        min_value=5,
        max_value=1024,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "建议 10-100 MB",
            }
        ),
    )

    upload_max_files = forms.IntegerField(
        label="每个项目允许上传的最大文件数",
        min_value=5,
        max_value=500,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "建议 10-50 个",
            }
        ),
    )

    session_timeout_minutes = forms.IntegerField(
        label="会话超时时间 (分钟)",
        min_value=5,
        max_value=1440,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "30 分钟 = 0.5 小时，1440 = 1 天",
            }
        ),
    )

    enable_audit_log = forms.BooleanField(
        label="启用操作审计日志",
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "role": "switch",
            }
        ),
    )

    enable_web_watermark = forms.BooleanField(
        label="启用网页水印",
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "role": "switch",
            }
        ),
    )

    web_watermark_opacity = forms.FloatField(
        label="水印透明度",
        min_value=0.05,
        max_value=0.5,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "0.05-0.5，建议 0.15",
                "step": "0.01",
            }
        ),
    )

    enable_export_watermark = forms.BooleanField(
        label="导出文件添加水印",
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "role": "switch",
            }
        ),
    )

    time_zone = forms.ChoiceField(
        label="时区",
        choices=[
            ("Asia/Shanghai", "Asia/Shanghai"),
        ],
        widget=forms.Select(),
    )


# class PermissionForm(forms.Form):
#     """权限编辑表单"""
