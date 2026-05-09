# -*- coding: utf-8 -*-
"""
Views 模块导出
保持与原 core/views.py 的函数签名完全兼容
"""

from .auth import login_view, logout_view
from .dashboard import dashboard, admin_dashboard
from .users import system_users, user_create, user_edit, user_delete
from .settings import (
    system_settings, system_permissions, 
    change_password, profile, profile_view, profile_settings, homepage_settings
)
from .taxonomy import (
    taxonomies, taxonomy_view, taxonomy_create, taxonomy_edit,
    taxonomy_delete, taxonomy_item_create, taxonomy_item_update, taxonomy_item_delete
)
from .importexport import importexport_dashboard
from .node import structure_dashboard
from .cron import cron_manager, cron_status, cron_run_task, cron_toggle_task, permission_check
from .api import (
    api_time_current, api_time_test, api_time_status,
    api_regions_provinces, api_regions_cities, api_regions_districts,
    api_regions_search, api_regions_path, api_regions_stats,
    api_dashboard_cards, api_dashboard_cards_save,
    api_nav_cards, api_nav_cards_save, navigation_settings
)
from .health import health_check, detailed_health_check, api_version
from .errors import error_400, error_403, error_404, error_500
from .logs import logs_index, logs_view
from .tools import tools_index, tools_page

__all__ = [
    'login_view', 'logout_view',
    'dashboard', 'admin_dashboard',
    'system_users', 'user_create', 'user_edit', 'user_delete',
    'system_settings', 'system_permissions',
    'change_password', 'profile', 'profile_view', 'profile_settings', 'homepage_settings',
    'taxonomies', 'taxonomy_view', 'taxonomy_create', 'taxonomy_edit',
    'taxonomy_delete', 'taxonomy_item_create', 'taxonomy_item_update', 'taxonomy_item_delete',
    'importexport_dashboard',
    'structure_dashboard',
    'cron_manager', 'cron_status', 'cron_run_task', 'cron_toggle_task', 'permission_check',
    'api_time_current', 'api_time_test', 'api_time_status',
    'api_regions_provinces', 'api_regions_cities', 'api_regions_districts',
    'api_regions_search', 'api_regions_path', 'api_regions_stats',
    'api_dashboard_cards', 'api_dashboard_cards_save',
    'api_nav_cards', 'api_nav_cards_save', 'navigation_settings',
    'health_check', 'detailed_health_check', 'api_version',
    'error_400', 'error_403', 'error_404', 'error_500',
    'logs_index', 'logs_view',
    'tools_index', 'tools_page',
]