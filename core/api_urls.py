# -*- coding: utf-8 -*-
"""
===============================================================================
文件：api_urls.py
路径：/home/edo/cimf/core/api_urls.py
===============================================================================

功能说明：
    REST API 版本化路由配置
    
    版本控制：
    - v1: 初始版本 (2026-)

版本：
    - 1.0: 初始版本

依赖：
    - core.views: 视图模块
"""

from django.urls import path
from core import views

app_name = 'api'

urlpatterns = [
    # Cron API
    path('cron/status/', views.cron_status, name='api_cron_status'),
    path('cron/run/<str:task_name>/', views.cron_run_task, name='api_cron_run_task'),
    path('cron/toggle/<str:task_name>/', views.cron_toggle_task, name='api_cron_toggle_task'),
    
    # 时间 API
    path('time/current/', views.api_time_current, name='api_time_current'),
    path('time/test/', views.api_time_test, name='api_time_test'),
    path('time/status/', views.api_time_status, name='api_time_status'),
    
    # 地区 API
    path('regions/provinces/', views.api_regions_provinces, name='api_regions_provinces'),
    path('regions/cities/', views.api_regions_cities, name='api_regions_cities'),
    path('regions/districts/', views.api_regions_districts, name='api_regions_districts'),
    path('regions/search/', views.api_regions_search, name='api_regions_search'),
    path('regions/path/', views.api_regions_path, name='api_regions_path'),
    path('regions/stats/', views.api_regions_stats, name='api_regions_stats'),
    
    # 功能卡片区域 API
    path('user/dashboard/cards/', views.api_dashboard_cards, name='api_dashboard_cards'),
    path('user/dashboard/cards/save/', views.api_dashboard_cards_save, name='api_dashboard_cards_save'),
    
    # 导航卡片
    path('user/nav-cards/', views.api_nav_cards, name='api_nav_cards'),
    path('user/nav-cards/save/', views.api_nav_cards_save, name='api_nav_cards_save'),
    
    # 健康检查
    path('health/', views.health_check, name='api_health_check'),
    path('health/detailed/', views.detailed_health_check, name='api_detailed_health_check'),
    path('version/', views.api_version, name='api_version'),
]