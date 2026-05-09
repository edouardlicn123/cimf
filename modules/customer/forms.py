# -*- coding: utf-8 -*-
"""
================================================================================
文件：forms.py
路径：/home/edo/cimf-v2/nodes/customer/forms.py
================================================================================

功能说明：
    客户表单定义

版本：
    - 1.0: 从 Flask WTForms 迁移为 Django Forms
"""

from django import forms


class CustomerForm(forms.Form):
    """客户表单"""
    
    customer_name = forms.CharField(
        label='客户名称',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入客户名称',
        })
    )
    
    contact_person = forms.CharField(
        label='联系人',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入联系人姓名',
        })
    )
    
    phone = forms.CharField(
        label='电话',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入电话号码',
        })
    )
    
    email = forms.EmailField(
        label='邮箱',
        max_length=100,
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入邮箱地址',
        })
    )
    
    address = forms.CharField(
        label='地址',
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入地址',
        })
    )
    
    notes = forms.CharField(
        label='备注',
        max_length=2000,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': '请输入备注',
            'rows': 4,
        })
    )
