# 文件路径：app/services/core/time_service.py
# 功能说明：时间服务 - 统一管理系统时间获取
# 说明：查询入口改为调用 TimeSyncService

from datetime import datetime
from app.services.core.settings_service import SettingsService
from app.services.core.time_sync_service import get_time_sync_service


class TimeService:
    """时间服务 - 统一管理系统时间获取"""

    @staticmethod
    def is_sync_enabled() -> bool:
        """是否启用时间同步"""
        return get_time_sync_service().is_enabled()

    @staticmethod
    def get_time_server_url() -> str:
        """获取配置的时间服务器URL"""
        return get_time_sync_service().get_server_url()

    @staticmethod
    def get_current_time() -> str:
        """获取当前时间（统一入口）"""
        return get_time_sync_service().get_current_time_str('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_current_datetime() -> datetime:
        """获取当前时间（datetime对象）"""
        return get_time_sync_service().get_current_time()

    @staticmethod
    def get_timezone() -> str:
        """获取配置的时区"""
        return SettingsService.get_setting('time_zone') or 'Asia/Shanghai'

    @staticmethod
    def get_sync_status() -> dict:
        """获取同步状态"""
        return get_time_sync_service().get_status()
