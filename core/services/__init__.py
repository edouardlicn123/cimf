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

from core.constants import UserRole

from .auth_service import AuthService
from .china_region_service import ChinaRegionService
from .cron_service import CronService, get_cron_service, init_cron_service
from .log_service import LogService
from .permission_service import PERMISSIONS, PermissionService
from .settings_service import SettingsService
from .taxonomy_service import TaxonomyService
from .time_service import TimeService
from .time_sync_service import TimeSyncService, get_time_sync_service
from .user_service import UserService
from .version_service import VersionService
from .watermark_service import WatermarkService

__all__ = [
    "PERMISSIONS",
    "AuthService",
    "ChinaRegionService",
    "CronService",
    "LogService",
    "PermissionService",
    "SettingsService",
    "TaxonomyService",
    "TimeService",
    "TimeSyncService",
    "UserRole",
    "UserService",
    "VersionService",
    "WatermarkService",
    "get_cron_service",
    "get_time_sync_service",
    "init_cron_service",
]
