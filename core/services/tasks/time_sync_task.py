# -*- coding: utf-8 -*-
"""
================================================================================
文件：time_sync_task.py
路径：/home/edo/cimf-v2/core/services/tasks/time_sync_task.py
================================================================================

功能说明：
    时间同步任务，定时与远程时间服务器同步系统时间。
    
版本：
    - 1.0: 从 Flask 迁移

依赖：
    - CronTask: 任务基类
"""

import logging
from .base import CronTask

logger = logging.getLogger(__name__)


class TimeSyncTask(CronTask):
    """
    时间同步任务类
    
    说明：
        定时与远程时间服务器同步系统时间，确保系统时间的准确性。
    """

    name = "time_sync"
    
    default_interval = 900  # 15分钟

    @property
    def setting_key_enabled(self) -> str:
        return "enable_time_sync"

    @property
    def setting_key_interval(self) -> str:
        return "time_sync_interval"

    def get_interval(self) -> int:
        """获取执行间隔（秒）"""
        try:
            from core.services import SettingsService
            interval = SettingsService.get_setting(self.setting_key_interval)
            if interval and isinstance(interval, int):
                return interval * 60  # 分钟转换为秒
        except Exception as e:
            logger.warning(f"获取时间同步间隔失败: {e}")
        return self.default_interval

    def execute(self):
        """执行时间同步"""
        from core.services import get_time_sync_service
        time_sync = get_time_sync_service()
        time_sync.sync_time()
