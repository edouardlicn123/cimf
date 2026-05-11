"""
API 模块导出
"""

from .cards import api_dashboard_cards, api_dashboard_cards_save, api_nav_cards, api_nav_cards_save, navigation_settings
from .regions import (
    api_regions_cities,
    api_regions_districts,
    api_regions_path,
    api_regions_provinces,
    api_regions_search,
    api_regions_stats,
)
from .time import api_time_current, api_time_status, api_time_test

__all__ = [
    'api_dashboard_cards',
    'api_dashboard_cards_save',
    'api_nav_cards',
    'api_nav_cards_save',
    'api_regions_cities',
    'api_regions_districts',
    'api_regions_path',
    'api_regions_provinces',
    'api_regions_search',
    'api_regions_stats',
    'api_time_current',
    'api_time_status',
    'api_time_test',
    'navigation_settings',
]
