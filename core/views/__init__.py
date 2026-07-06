"""
Views 模块导出
保持与原 core/views.py 的函数签名完全兼容
"""

from .api import (
    api_dashboard_cards,
    api_dashboard_cards_save,
    api_nav_cards,
    api_nav_cards_save,
    api_regions_cities,
    api_regions_districts,
    api_regions_path,
    api_regions_provinces,
    api_regions_search,
    api_regions_stats,
    api_time_current,
    api_time_status,
    api_time_test,
    navigation_settings,
)
from .auth import login_view, logout_view
from .cron import cron_manager, cron_run_task, cron_status, cron_toggle_task, permission_check
from .dashboard import admin_dashboard, dashboard
from .errors import error_400, error_403, error_404, error_500
from .health import api_version, detailed_health_check, health_check
from .importexport import importexport_dashboard
from .logs import logs_index, logs_view
from .node import structure_dashboard
from .settings import (
    change_password,
    homepage_settings,
    profile,
    profile_settings,
    profile_view,
    system_permissions,
    system_settings,
)
from .taxonomy import (
    taxonomies,
    taxonomy_create,
    taxonomy_delete,
    taxonomy_edit,
    taxonomy_item_create,
    taxonomy_item_delete,
    taxonomy_item_update,
    taxonomy_view,
)
from .tools import tools_index, tools_page
from .users import system_users, user_create, user_delete, user_edit

__all__ = [
    "admin_dashboard",
    "api_dashboard_cards",
    "api_dashboard_cards_save",
    "api_nav_cards",
    "api_nav_cards_save",
    "api_regions_cities",
    "api_regions_districts",
    "api_regions_path",
    "api_regions_provinces",
    "api_regions_search",
    "api_regions_stats",
    "api_time_current",
    "api_time_status",
    "api_time_test",
    "api_version",
    "cron_manager",
    "cron_run_task",
    "cron_status",
    "cron_toggle_task",
    "dashboard",
    "detailed_health_check",
    "error_400",
    "error_403",
    "error_404",
    "error_500",
    "health_check",
    "homepage_settings",
    "importexport_dashboard",
    "login_view",
    "logout_view",
    "logs_index",
    "logs_view",
    "navigation_settings",
    "permission_check",
    "profile_settings",
    "profile_view",
    "structure_dashboard",
    "system_permissions",
    "system_settings",
    "system_users",
    "taxonomies",
    "taxonomy_create",
    "taxonomy_delete",
    "taxonomy_edit",
    "taxonomy_item_create",
    "taxonomy_item_delete",
    "taxonomy_item_update",
    "taxonomy_view",
    "tools_index",
    "tools_page",
    "user_create",
    "user_delete",
    "user_edit",
]
