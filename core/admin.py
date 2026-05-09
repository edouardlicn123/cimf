# -*- coding: utf-8 -*-
"""
================================================================================
文件：admin.py
路径：/home/edo/cimf-v2/core/admin.py
================================================================================

功能说明：
    Django Admin 配置，用于管理后台数据管理界面。
    
    参考 Flask 版本设计：
    - 系统用户管理
    - 系统设置管理
    - 词汇表管理

版本：
    - 1.0: 初始版本，从 Flask 迁移

依赖：
    - django.contrib.admin: Admin 框架
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, SystemSetting, Taxonomy, TaxonomyItem


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    用户管理后台配置
    
    参考 Flask 版本设计：
    - 列表页显示：用户名、昵称、角色、状态、最后登录时间
    - 支持搜索、过滤
    """
    
    list_display = ['username', 'nickname', 'role', 'is_active', 'is_admin', 'last_login_at', 'created_at']
    list_filter = ['role', 'is_active', 'is_admin', 'is_staff', 'created_at']
    search_fields = ['username', 'nickname', 'email']
    ordering = ['-id']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'password', 'nickname', 'email')
        }),
        ('角色与权限', {
            'fields': ('role', 'is_admin', 'is_active', 'is_staff', 'is_superuser', 'permissions')
        }),
        ('个人偏好', {
            'fields': ('theme', 'notifications_enabled', 'preferred_language')
        }),
        ('安全设置', {
            'fields': ('failed_login_attempts', 'locked_until')
        }),
        ('时间记录', {
            'fields': ('last_login_at', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['failed_login_attempts', 'locked_until', 'last_login_at', 'created_at', 'updated_at']
    
    add_fieldsets = (
        ('基本信息', {
            'fields': ('username', 'password1', 'password2', 'nickname', 'email')
        }),
        ('角色与权限', {
            'fields': ('role', 'is_admin', 'is_active')
        }),
    )


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    """
    系统设置管理后台配置
    
    参考 Flask 版本设计：
    - 列表页显示：键名、值、描述、更新时间
    - 支持搜索、编辑
    """
    
    list_display = ['key', 'value', 'description', 'updated_at']
    search_fields = ['key', 'description']
    ordering = ['key']
    
    fieldsets = (
        ('配置信息', {
            'fields': ('key', 'value', 'description')
        }),
    )
    
    readonly_fields = ['updated_at']


class TaxonomyItemInline(admin.TabularInline):
    """
    词汇项内联编辑
    """
    model = TaxonomyItem
    extra = 1
    fields = ['name', 'description', 'weight']
    ordering = ['weight', 'name']


@admin.register(Taxonomy)
class TaxonomyAdmin(admin.ModelAdmin):
    """
    词汇表管理后台配置
    
    参考 Flask 版本设计：
    - 列表页显示：名称、标识符、描述、创建时间
    - 支持内联编辑词汇项
    """
    
    list_display = ['name', 'slug', 'description', 'created_at']
    search_fields = ['name', 'slug', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('词汇表信息', {
            'fields': ('name', 'slug', 'description')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    inlines = [TaxonomyItemInline]


@admin.register(TaxonomyItem)
class TaxonomyItemAdmin(admin.ModelAdmin):
    """
    词汇项管理后台配置
    """
    
    list_display = ['name', 'taxonomy', 'weight', 'description', 'created_at']
    list_filter = ['taxonomy']
    search_fields = ['name', 'description']
    ordering = ['taxonomy', 'weight', 'name']
    
    fieldsets = (
        ('词汇项信息', {
            'fields': ('taxonomy', 'name', 'description', 'weight')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
