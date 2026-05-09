# -*- coding: utf-8 -*-
"""
海外客户 Admin 配置
"""

from django.contrib import admin
from .models import CustomerFields


@admin.register(CustomerFields)
class CustomerFieldsAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'enterprise_name', 'phone1', 'email1', 'customer_type', 'customer_level', 'created_at']
    list_filter = ['customer_type', 'customer_level', 'created_at']
    search_fields = ['customer_name', 'enterprise_name', 'phone1', 'phone2', 'email1', 'email2']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('node', 'customer_name', 'customer_code', 'customer_type', 'enterprise_name')
        }),
        ('联系方式1', {
            'fields': ('phone1', 'email1')
        }),
        ('联系方式2', {
            'fields': ('phone2', 'email2')
        }),
        ('地址信息', {
            'fields': ('country', 'province', 'address', 'postal_code')
        }),
        ('企业信息', {
            'fields': ('industry', 'enterprise_type', 'registered_capital')
        }),
        ('其他', {
            'fields': ('customer_level', 'credit_limit', 'website', 'notes')
        }),
        ('时间', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
