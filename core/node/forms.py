# -*- coding: utf-8 -*-
"""
================================================================================
文件：forms.py
路径：/home/edo/cimf-v2/core/node/forms.py
================================================================================

功能说明：
    Node 节点系统表单定义

版本：
    - 1.0: 从 modules/forms.py 迁移

依赖：
    - django.forms: 表单框架
"""

from django import forms


class NodeTypeForm(forms.Form):
    """节点类型表单"""
    
    name = forms.CharField(
        label='节点类型名称',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入节点类型名称',
        })
    )
    
    slug = forms.SlugField(
        label='标识符',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入 URL 标识符（英文、数字、下划线）',
        })
    )
    
    description = forms.CharField(
        label='描述',
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': '请输入描述',
            'rows': 3,
        })
    )
    
    icon = forms.CharField(
        label='图标',
        max_length=50,
        initial='bi-folder',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bootstrap Icons 类名',
        })
    )