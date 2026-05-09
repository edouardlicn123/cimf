# -*- coding: utf-8 -*-
"""
================================================================================
文件：__init__.py
路径：/home/edo/cimf-v2/core/services/__init__.py
================================================================================

功能说明：
    核心服务层模块导出

版本：
    - 1.0: 初始版本
    - 1.1: 添加 CronService, TimeSyncService
    - 1.2: 添加 ChinaRegionService

导出：
    - SettingsService: 系统设置服务
    - PermissionService: 权限服务
    - UserService: 用户服务
    - AuthService: 认证服务
    - CronService: 定时任务服务
    - TimeSyncService: 时间同步服务
    - TaxonomyService: 词汇表服务
    - ChinaRegionService: 中国行政区划服务
"""

from .settings_service import SettingsService
from .permission_service import PermissionService, PERMISSIONS
from core.constants import UserRole
from .user_service import UserService
from .auth_service import AuthService
from .cron_service import CronService, get_cron_service, init_cron_service
from .time_sync_service import TimeSyncService, get_time_sync_service
from .time_service import TimeService
from .watermark_service import WatermarkService
from .taxonomy_service import TaxonomyService
from .china_region_service import ChinaRegionService
from .version_service import VersionService
from .log_service import LogService

__all__ = [
    'SettingsService',
    'PermissionService',
    'UserService',
    'AuthService',
    'UserRole',
    'PERMISSIONS',
    'CronService',
    'get_cron_service',
    'init_cron_service',
    'TimeSyncService',
    'get_time_sync_service',
    'TimeService',
    'WatermarkService',
    'TaxonomyService',
    'ChinaRegionService',
    'VersionService',
    'LogService',
]
