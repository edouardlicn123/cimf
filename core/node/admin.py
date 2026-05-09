# -*- coding: utf-8 -*-
"""
================================================================================
文件：admin.py
路径：/home/edo/cimf-v2/core/node/admin.py
================================================================================

功能说明：
    Node 节点系统 Django Admin 配置

版本：
    - 1.0: 从 modules/admin.py 迁移

依赖：
    - core.node.models: NodeType, Node
"""

from django.contrib import admin
from core.node.models import NodeType, Node


@admin.register(NodeType)
class NodeTypeAdmin(admin.ModelAdmin):
    """节点类型管理"""
    list_display = ['name', 'slug', 'icon', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'slug', 'description', 'icon')
        }),
        ('配置', {
            'fields': ('fields_config', 'is_active')
        }),
        ('时间', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    """节点管理"""
    list_display = ['id', 'node_type', 'created_by', 'created_at', 'updated_at']
    list_filter = ['node_type', 'created_at']
    search_fields = ['id']
    ordering = ['-created_at']
    
    fieldsets = (
        ('节点信息', {
            'fields': ('node_type',)
        }),
        ('用户信息', {
            'fields': ('created_by', 'updated_by')
        }),
        ('时间', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']