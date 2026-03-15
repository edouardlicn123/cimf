# -*- coding: utf-8 -*-
"""
================================================================================
文件：app/services/core/time_service.py
路径：/home/edo/cimf-v2/app/services/core/time_service.py
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
    - 1.0: 初始版本

依赖：
    - TimeSyncService: 时间同步服务
    - SettingsService: 系统设置服务
"""

from datetime import datetime
from app.services.core.settings_service import SettingsService
from app.services.core.time_sync_service import get_time_sync_service


# =============================================================================
# TimeService 类
# =============================================================================

class TimeService:
    """
    时间服务类
    
    说明：
        作为时间相关功能的统一入口，封装了 TimeSyncService 的功能。
        提供静态方法，无需实例化即可使用。
    """

    # -------------------------------------------------------------------------
    # 时间同步
    # -------------------------------------------------------------------------

    @staticmethod
    def is_sync_enabled() -> bool:
        """
        检查时间同步是否启用
        
        返回：
            是否启用时间同步
        """
        return get_time_sync_service().is_enabled()

    @staticmethod
    def get_time_server_url() -> str:
        """
        获取配置的时间服务器 URL
        
        返回：
            时间服务器 URL 字符串
        """
        return get_time_sync_service().get_server_url()

    # -------------------------------------------------------------------------
    # 时间获取
    # -------------------------------------------------------------------------

    @staticmethod
    def get_current_time() -> str:
        """
        获取当前时间字符串（统一入口）
        
        说明：
            返回格式化的当前时间字符串。
            如果时间同步成功，返回同步后的时间；
            否则返回本地时间。
        
        返回：
            格式：'YYYY-MM-DD HH:MM:SS'
        """
        return get_time_sync_service().get_current_time_str('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_current_datetime() -> datetime:
        """
        获取当前时间（datetime 对象）
        
        说明：
            如果时间同步成功，返回同步后的时间加上流逝时间；
            否则返回本地时间。
        
        返回：
            datetime 对象
        """
        return get_time_sync_service().get_current_time()

    # -------------------------------------------------------------------------
    # 时区
    # -------------------------------------------------------------------------

    @staticmethod
    def get_timezone() -> str:
        """
        获取配置的时区
        
        返回：
            时区字符串，如 'Asia/Shanghai'
        """
        return SettingsService.get_setting('time_zone') or 'Asia/Shanghai'

    # -------------------------------------------------------------------------
    # 状态
    # -------------------------------------------------------------------------

    @staticmethod
    def get_sync_status() -> dict:
        """
        获取时间同步状态
        
        返回：
            包含同步状态的字典：
            - status: 同步状态 ('never', 'success', 'failed')
            - synced_time: 上次同步成功的时间
            - last_sync_timestamp: 上次同步的时间戳
            - enabled: 是否启用
        """
        return get_time_sync_service().get_status()
