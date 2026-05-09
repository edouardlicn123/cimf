# -*- coding: utf-8 -*-
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
from core.models import User
from core.constants import UserTheme, Language


class ProfileForm(forms.Form):
    """个人信息编辑表单（昵称、邮箱）"""
    
    nickname = forms.CharField(
        label='显示昵称',
        max_length=64,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '用于仪表盘，项目成员列表等的友好显示名称（可留空）',
            'autocomplete': 'nickname',
        })
    )
    
    email = forms.EmailField(
        label='邮箱地址',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '用于密码重置，系统通知、找回账号（可留空）',
            'autocomplete': 'email',
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip()
            if self.user_id:
                if User.objects.filter(email=email).exclude(id=self.user_id).exists():
                    raise ValidationError('该邮箱已被其他用户使用，请更换')
            else:
                if User.objects.filter(email=email).exists():
                    raise ValidationError('该邮箱已被其他用户使用，请更换')
        return email


class PreferencesForm(forms.Form):
    """用户偏好设置表单（主题、通知，语言）"""
    
    theme = forms.ChoiceField(
        label='界面主题',
        choices=UserTheme.DISPLAY_LABELS.items(),
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
        })
    )
    
    notifications_enabled = forms.BooleanField(
        label='开启系统通知',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch',
            'id': 'notificationsSwitch',
        })
    )
    
    preferred_language = forms.ChoiceField(
        label='界面语言',
        choices=Language.CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
        })
    )


class ChangePasswordForm(forms.Form):
    """修改密码表单 - 安全强化版"""
    
    current_password = forms.CharField(
        label='当前密码 *',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '请输入当前密码以验证身份',
            'autocomplete': 'current-password',
        })
    )
    
    new_password = forms.CharField(
        label='新密码 *',
        min_length=10,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '建议 12+ 字符，包含大小写，数字、符号',
            'autocomplete': 'new-password',
        })
    )
    
    confirm_password = forms.CharField(
        label='确认新密码 *',
        min_length=10,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '请再次输入新密码',
            'autocomplete': 'new-password',
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if current_password and self.user:
            if not self.user.check_password(current_password):
                raise ValidationError('当前密码输入错误，请重试')
        return current_password
    
    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        # 如果填写了新密码，必须填写当前密码
        if new_password and not current_password:
            raise ValidationError('修改密码时必须填写当前密码')
        
        if new_password:
            if not confirm_password:
                raise ValidationError('请确认新密码')
            if new_password != confirm_password:
                raise ValidationError('两次输入的新密码不一致')
            if len(new_password) < 10:
                raise ValidationError('新密码长度至少 10 个字符（建议 12+ 字符）')
        
        return cleaned_data
