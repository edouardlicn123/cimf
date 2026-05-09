# -*- coding: utf-8 -*-
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
from core.models import User
from core.constants import UserRole
from core.forms.mixins import BootstrapFormMixin


class UserSearchForm(forms.Form):
    """用户搜索表单"""
    
    username = forms.CharField(
        label='用户名 / 昵称',
        max_length=64,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '输入用户名或昵称搜索（支持模糊匹配）',
        })
    )
    
    is_active = forms.BooleanField(
        label='仅显示启用用户',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch',
        })
    )


class UserCreateForm(BootstrapFormMixin, forms.ModelForm):
    """用户创建表单"""
    
    password = forms.CharField(
        label='密码',
        min_length=10,
        widget=forms.PasswordInput(attrs={
            'placeholder': '用于登录的唯一账号（10+ 字符）',
            'autocomplete': 'new-password',
        })
    )
    
    confirm_password = forms.CharField(
        label='确认密码',
        min_length=10,
        widget=forms.PasswordInput(attrs={
            'placeholder': '请再次输入密码以确认',
            'autocomplete': 'new-password',
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'nickname', 'email', 'role', 'is_admin']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': '用于登录的唯一账号（3-64 字符）',
                'autocomplete': 'username',
            }),
            'nickname': forms.TextInput(attrs={
                'placeholder': '仪表盘、项目成员列表等处显示的友好名称',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': '用于密码重置、系统通知（可留空）',
                'autocomplete': 'email',
            }),
            'is_admin': forms.CheckboxInput(attrs={
                'role': 'switch',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = UserRole.CHOICES
        self.fields['role'].initial = UserRole.EMPLOYEE
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = username.strip()
            if User.objects.filter(username=username).exists():
                raise ValidationError('该用户名已被占用，请更换其他用户名')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip()
            if User.objects.filter(email=email).exists():
                raise ValidationError('该邮箱已被其他用户使用')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        # 如果填写了密码，必须填写确认密码
        if password:
            if not confirm_password:
                raise ValidationError('请确认密码')
            if password != confirm_password:
                raise ValidationError('两次输入的密码不一致')
            if len(password) < 10:
                raise ValidationError('密码长度至少 10 个字符（建议 12+ 字符）')
        
        return cleaned_data


class UserEditForm(BootstrapFormMixin, forms.ModelForm):
    """用户编辑表单"""
    
    password = forms.CharField(
        label='新密码',
        required=False,
        min_length=10,
        widget=forms.PasswordInput(attrs={
            'placeholder': '编辑时留空则不修改密码',
            'autocomplete': 'new-password',
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'nickname', 'email', 'role', 'is_admin', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': '用于登录的唯一账号（3-64 字符）',
                'autocomplete': 'username',
                'readonly': True,
            }),
            'nickname': forms.TextInput(attrs={
                'placeholder': '仪表盘、项目成员列表等处显示的友好名称',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': '用于密码重置、系统通知（可留空）',
                'autocomplete': 'email',
            }),
            'is_admin': forms.CheckboxInput(attrs={
                'role': 'switch',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'role': 'switch',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = UserRole.CHOICES
        if self.instance and self.instance.pk:
            self._original_username = self.instance.username
        else:
            self._original_username = None
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = username.strip()
            if self._original_username and username != self._original_username:
                raise ValidationError('用户名不可修改')
            if self.user_id:
                if User.objects.filter(username=username).exclude(id=self.user_id).exists():
                    raise ValidationError('该用户名已被占用，请更换其他用户名')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip()
            if self.user_id:
                if User.objects.filter(email=email).exclude(id=self.user_id).exists():
                    raise ValidationError('该邮箱已被其他用户使用')
            else:
                if User.objects.filter(email=email).exists():
                    raise ValidationError('该邮箱已被其他用户使用')
        return email


class SystemSettingsForm(forms.Form):
    """系统设置表单"""
    
    system_name = forms.CharField(
        label='系统名称',
        max_length=60,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '显示在导航栏和页面标题',
        })
    )
    
    upload_max_size_mb = forms.IntegerField(
        label='单个文件最大上传大小 (MB)',
        min_value=5,
        max_value=1024,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '建议 10-100 MB',
        })
    )
    
    upload_max_files = forms.IntegerField(
        label='每个项目允许上传的最大文件数',
        min_value=5,
        max_value=500,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '建议 10-50 个',
        })
    )
    
    session_timeout_minutes = forms.IntegerField(
        label='会话超时时间 (分钟)',
        min_value=5,
        max_value=1440,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '30 分钟 = 0.5 小时，1440 = 1 天',
        })
    )
    
    enable_audit_log = forms.BooleanField(
        label='启用操作审计日志',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch',
        })
    )
    
    enable_web_watermark = forms.BooleanField(
        label='启用网页水印',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch',
        })
    )
    
    web_watermark_opacity = forms.FloatField(
        label='水印透明度',
        min_value=0.05,
        max_value=0.5,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '0.05-0.5，建议 0.15',
            'step': '0.01',
        })
    )
    
    enable_export_watermark = forms.BooleanField(
        label='导出文件添加水印',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch',
        })
    )
    
    time_zone = forms.ChoiceField(
        label='时区',
        choices=[
            ('Asia/Shanghai', 'Asia/Shanghai'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
        })
    )


class PermissionForm(forms.Form):
    """权限编辑表单"""
    pass
