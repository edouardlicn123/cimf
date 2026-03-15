# 文件路径：app/services/core/tasks/time_sync_task.py
# 功能说明：时间同步任务
# 版本：1.1
# 更新日期：2026-03-15

from app.services.core.tasks.base import CronTask, _get_settings_service
import logging

logger = logging.getLogger(__name__)


class TimeSyncTask(CronTask):
    """时间同步任务"""

    name = "time_sync"
    default_interval = 900

    @property
    def setting_key_enabled(self) -> str:
        return "enable_time_sync"

    @property
    def setting_key_interval(self) -> str:
        return "time_sync_interval"

    def get_interval(self) -> int:
        """获取执行间隔（秒）- 从分钟转换"""
        try:
            SettingsService = _get_settings_service()
            interval = SettingsService.get_setting(self.setting_key_interval)
            if interval and isinstance(interval, int):
                return interval * 60
        except Exception as e:
            logger.warning(f"获取时间同步间隔失败: {e}")
        return self.default_interval

    def execute(self):
        """执行时间同步"""
        from app.services.core.time_sync_service import get_time_sync_service
        time_sync = get_time_sync_service()
        time_sync.sync_time()
