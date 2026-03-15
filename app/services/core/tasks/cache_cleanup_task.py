# 文件路径：app/services/core/tasks/cache_cleanup_task.py
# 功能说明：缓存清理任务
# 版本：1.2
# 更新日期：2026-03-15

from app.services.core.tasks.base import CronTask, _get_settings_service
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheCleanupTask(CronTask):
    """缓存清理任务"""

    name = "cache_cleanup"
    default_interval = 10800  # 3小时

    @property
    def setting_key_enabled(self) -> str:
        return "cron_cache_cleanup_enabled"

    @property
    def setting_key_interval(self) -> str:
        return "cron_cache_cleanup_interval"

    def execute(self):
        """执行缓存清理"""
        if self._last_run and (datetime.now() - self._last_run) < timedelta(seconds=10):
            logger.info(f"缓存清理任务跳过：上次执行在10秒内")
            return
        
        SettingsService = _get_settings_service()
        SettingsService.clear_cache()
        logger.info("缓存清理任务执行完成")
