# -*- coding: utf-8 -*-
"""
================================================================================
文件：time_service.py
路径：/home/edo/cimf-v2/core/services/time_service.py
================================================================================

功能说明：
    时间服务 - 统一管理系统时间获取的入口
    
    主要功能：
    - 提供统一的时间获取接口
    - 封装 TimeSyncService 的功能
    - 提供时间同步状态查询
    
    设计说明：
        此服务是时间相关功能的统一入口，调用 TimeSyncService 完成实际工作。
        前端或其他模块应使用此服务获取时间，而不是直接调用 TimeSyncService。

用法：
    1. 获取当前时间字符串：
        now = TimeService.get_current_time()  # 返回 '2024-01-01 12:00:00'
    
    2. 获取当前时间 datetime 对象：
        now = TimeService.get_current_datetime()
    
    3. 检查同步是否启用：
        enabled = TimeService.is_sync_enabled()
    
    4. 获取同步状态：
        status = TimeService.get_sync_status()
    
    5. 获取时区：
        tz = TimeService.get_timezone()

版本：
    - 1.0: 从 Flask 迁移

依赖：
    - TimeSyncService: 时间同步服务
    - SettingsService: 系统设置服务
"""

from datetime import datetime
from .settings_service import SettingsService
from .time_sync_service import get_time_sync_service


class TimeService:
    """
    时间服务类
    
    说明：
        作为时间相关功能的统一入口，封装了 TimeSyncService 的功能。
        提供静态方法，无需实例化即可使用。
    """

    @staticmethod
    def is_sync_enabled() -> bool:
        """检查时间同步是否启用"""
        return get_time_sync_service().is_enabled()

    @staticmethod
    def get_time_server_url() -> str:
        """获取配置的时间服务器 URL"""
        return get_time_sync_service().get_server_url()

    @staticmethod
    def get_current_time() -> str:
        """获取当前时间字符串（统一入口）"""
        return get_time_sync_service().get_current_time_str('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_current_datetime() -> datetime:
        """获取当前时间（datetime 对象）"""
        return get_time_sync_service().get_current_time()

    @staticmethod
    def get_timezone() -> str:
        """获取配置的时区"""
        return SettingsService.get_setting('time_zone') or 'Asia/Shanghai'

    @staticmethod
    def get_sync_status() -> dict:
        """获取时间同步状态"""
        return get_time_sync_service().get_status()
