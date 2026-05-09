# -*- coding: utf-8 -*-
"""
核心应用 URL 路由配置
"""

from django.urls import path, re_path, include
from django.views.generic.base import RedirectView
from . import views
from core.smtp import views as smtp_views
from core.node import views as node_views
from core.node.views import field_types, field_types_api

app_name = 'core'

urlpatterns = [
    # 认证
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    
    # 仪表盘
    path('', views.dashboard, name='dashboard'),
    
    # 内容结构
    path('structure/dashboard/', views.structure_dashboard, name='structure_dashboard'),
    path('structure/types/', node_views.node_types_list, name='node_types_list'),
    path('structure/types/<int:node_type_id>/toggle/', node_views.node_type_toggle, name='node_type_toggle'),
    path('structure/types/<int:node_type_id>/delete/', node_views.node_type_delete, name='node_type_delete'),
    path('structure/fieldtypes/', field_types, name='field_types'),
    path('structure/api/fieldtypes/', field_types_api, name='field_types_api'),
    path('structure/taxonomies/', views.taxonomies, name='taxonomies'),
    path('structure/taxonomy/<int:taxonomy_id>/', views.taxonomy_view, name='taxonomy_view'),
    path('structure/taxonomy/<int:taxonomy_id>/edit/', views.taxonomy_edit, name='taxonomy_edit'),
    path('structure/taxonomy/create/', views.taxonomy_create, name='taxonomy_create'),
    path('structure/taxonomy/<int:taxonomy_id>/delete/', views.taxonomy_delete, name='taxonomy_delete'),
    path('structure/taxonomy/<int:taxonomy_id>/item/create/', views.taxonomy_item_create, name='taxonomy_item_create'),
    path('structure/taxonomy/<int:taxonomy_id>/item/<int:item_id>/edit/', views.taxonomy_item_update, name='taxonomy_item_update'),
    path('structure/taxonomy/<int:taxonomy_id>/item/<int:item_id>/delete/', views.taxonomy_item_delete, name='taxonomy_item_delete'),
    
    # 协作工具
    path('tools/dashboard/', views.tools_index, name='tools_index'),
    re_path(r'^tools/(?P<tool_slug>[\w-]+)/$', views.tools_page, name='tools_page'),
    
    # 系统管理
    path('system/', views.admin_dashboard, name='admin_dashboard'),
    path('system/users/', views.system_users, name='system_users'),
    path('system/user/create/', views.user_create, name='user_create'),
    path('system/user/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('system/user/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('system/settings/', views.system_settings, name='system_settings'),
    path('system/permissions/', views.system_permissions, name='system_permissions'),
    path('system/cron/', views.cron_manager, name='cron_manager'),
    path('system/permission-check/', views.permission_check, name='permission_check'),
    path('system/smtp/', smtp_views.smtp_config, name='smtp_config'),
    path('system/smtp/test/', smtp_views.smtp_test, name='smtp_test'),
    path('system/smtp/history/', smtp_views.smtp_history, name='smtp_history'),
    path('system/smtp/cleanup/', smtp_views.smtp_cleanup_logs, name='smtp_cleanup_logs'),
    path('system/logs/', views.logs_index, name='logs_index'),
    path('system/logs/<str:log_type>/', views.logs_view, name='logs_view'),
    
    # 个人中心
    path('user/profile/', views.profile_view, name='profile_view'),
    path('user/settings/', views.profile_settings, name='profile_settings'),
    path('user/functioncards/', views.homepage_settings, name='homepage_settings'),
    path('user/navcards/', views.navigation_settings, name='navigation_settings'),
    
    # 健康检查
    path('health/', views.health_check, name='health_check'),
    path('health/detailed/', views.detailed_health_check, name='detailed_health_check'),
    
    # 旧路径重定向（向后兼容）
    path('structure/', RedirectView.as_view(url='/structure/dashboard/', permanent=False)),
    path('taxonomies/', RedirectView.as_view(url='/structure/taxonomies/', permanent=False)),
    path('taxonomy/', RedirectView.as_view(url='/structure/taxonomies/', permanent=False)),
]
