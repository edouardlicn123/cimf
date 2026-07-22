"""
================================================================================
文件：settings_forms.py
路径：/home/edo/cimf-v2/core/forms/settings_forms.py
================================================================================

功能说明：
    用户设置相关 Django 表单定义，包括个人信息编辑、偏好设置、
    修改密码三个表单

版本：
    - 1.0: 从 Flask WTForms 迁移为 Django Forms

依赖：
    - django.forms: Django 表单
    - django.contrib.auth: 认证
"""

from django import forms
from django.core.exceptions import ValidationError

from core.constants import Language, UserTheme
from core.forms.mixins import (
    _USER_FORM_WIDGETS,
    BootstrapFormMixin,
    EmailCleanMixin,
    UserAwareFormMixin,
)
from core.forms.validators import validate_password_confirmation


class ProfileForm(BootstrapFormMixin, EmailCleanMixin, UserAwareFormMixin, forms.Form):
    """个人信息编辑表单（昵称、邮箱）"""

    nickname = forms.CharField(
        label="显示昵称",
        max_length=64,
        required=False,
        widget=_USER_FORM_WIDGETS["nickname"],
    )

    email = forms.EmailField(
        label="邮箱地址",
        required=False,
        widget=_USER_FORM_WIDGETS["email"],
    )


class PreferencesForm(BootstrapFormMixin, forms.Form):
    """用户偏好设置表单（主题、通知，语言）"""

    theme = forms.ChoiceField(
        label="界面主题",
        choices=UserTheme.DISPLAY_LABELS.items(),
        widget=forms.Select(),
    )

    notifications_enabled = forms.BooleanField(
        label="开启系统通知",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={
                "role": "switch",
                "id": "notificationsSwitch",
            }
        ),
    )

    preferred_language = forms.ChoiceField(
        label="界面语言",
        choices=Language.CHOICES,
        widget=forms.Select(),
    )


class ChangePasswordForm(BootstrapFormMixin, UserAwareFormMixin, forms.Form):
    """修改密码表单 - 安全强化版"""

    current_password = forms.CharField(
        label="当前密码 *",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "请输入当前密码以验证身份",
                "autocomplete": "current-password",
            }
        ),
    )

    new_password = forms.CharField(
        label="新密码 *",
        min_length=10,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "建议 12+ 字符，包含大小写，数字、符号",
                "autocomplete": "new-password",
            }
        ),
    )

    confirm_password = forms.CharField(
        label="确认新密码 *",
        min_length=10,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "请再次输入新密码",
                "autocomplete": "new-password",
            }
        ),
    )

    def clean_current_password(self):
        current_password = self.cleaned_data.get("current_password")
        if current_password:
            if not self.user:
                raise ValidationError("用户信息缺失，无法验证密码")
            if not self.user.check_password(current_password):
                raise ValidationError("当前密码输入错误，请重试")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password:
            validate_password_confirmation(new_password, confirm_password)

        return cleaned_data
