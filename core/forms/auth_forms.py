# -*- coding: utf-8 -*-
"""
================================================================================
文件：auth_forms.py
路径：/home/edo/cimf-v2/core/forms/auth_forms.py
================================================================================

功能说明：
    认证相关 Django 表单定义，包括登录表单

版本：
    - 1.0: 从 Flask WTForms 迁移为 Django Forms

依赖：
    - django.forms: Django 表单
"""

from django import forms
from django.core.validators import MinLengthValidator


class LoginForm(forms.Form):
    """登录表单"""
    
    username = forms.CharField(
        label='用户名',
        max_length=64,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '请输入用户名',
            'autocomplete': 'username',
            'autofocus': True,
        })
    )
    
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '请输入密码',
            'autocomplete': 'current-password',
        })
    )
    
    remember_me = forms.BooleanField(
        label='记住我',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch',
        })
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            return username.strip()
        return username
