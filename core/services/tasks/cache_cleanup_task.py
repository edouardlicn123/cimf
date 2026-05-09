# -*- coding: utf-8 -*-
"""
================================================================================
文件：cache_cleanup_task.py
路径：/home/edo/cimf-v2/core/services/tasks/cache_cleanup_task.py
================================================================================

功能说明：
    缓存清理任务，定时清理系统缓存数据。
    
版本：
    - 1.0: 从 Flask 迁移

依赖：
    - CronTask: 任务基类
"""

import logging
from datetime import timedelta
from django.utils.timezone import now
from .base import CronTask

logger = logging.getLogger(__name__)


class CacheCleanupTask(CronTask):
    """
    缓存清理任务类
    
    说明：
        定时清理系统缓存，释放内存资源。
    """

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
        if self._last_run and (now() - self._last_run) < timedelta(seconds=10):
            logger.info("缓存清理任务跳过：上次执行在10秒内")
            return
        
        from core.services import SettingsService
        SettingsService.clear_cache()
        logger.info("缓存清理任务执行完成")
