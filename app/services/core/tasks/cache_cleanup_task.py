# -*- coding: utf-8 -*-
"""
================================================================================
文件：app/services/core/tasks/cache_cleanup_task.py
路径：/home/edo/cimf-v2/app/services/core/tasks/cache_cleanup_task.py
================================================================================

功能说明：
    缓存清理任务，定时清理系统缓存数据。
    
    主要功能：
    - 清理 SettingsService 的内部缓存
    - 可配置执行间隔（默认3小时）
    - 从系统设置读取配置
    
    此任务是 CronService 管理的具体任务实现之一。

用法：
    1. 注册到 CronService：
        from app.services.core.cron_service import get_cron_service
        from app.services.core.tasks import CacheCleanupTask
        cron = get_cron_service()
        cron.register(CacheCleanupTask())
    
    2. 通过系统设置配置：
        - cron_cache_cleanup_enabled: 是否启用（默认 true）
        - cron_cache_cleanup_interval: 执行间隔秒数（默认 10800 = 3小时）

版本：
    - 1.0: 初始版本
    - 1.1: 添加防重复执行检查
    - 1.2: 优化导入方式

依赖：
    - CronTask: 任务基类
    - SettingsService: 系统设置服务
"""

from app.services.core.tasks.base import CronTask, _get_settings_service
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# CacheCleanupTask 类
# =============================================================================

class CacheCleanupTask(CronTask):
    """
    缓存清理任务类
    
    说明：
        定时清理系统缓存，释放内存资源。
        默认每3小时执行一次，可通过系统设置调整。
    """

    # 任务名称
    name = "cache_cleanup"
    
    # 默认执行间隔：3小时（10800秒）
    default_interval = 10800

    @property
    def setting_key_enabled(self) -> str:
        """
        获取启用设置项的 key
        
        返回：
            'cron_cache_cleanup_enabled'
        """
        return "cron_cache_cleanup_enabled"

    @property
    def setting_key_interval(self) -> str:
        """
        获取间隔设置项的 key
        
        返回：
            'cron_cache_cleanup_interval'
        """
        return "cron_cache_cleanup_interval"

    def execute(self):
        """
        执行缓存清理
        
        说明：
            调用 SettingsService.clear_cache() 清理缓存。
            为防止频繁执行，此方法内部还会检查上次执行时间，
            如果10秒内执行过则跳过。
        """
        # 双重保护：方法级别防重复
        if self._last_run and (datetime.now() - self._last_run) < timedelta(seconds=10):
            logger.info("缓存清理任务跳过：上次执行在10秒内")
            return
        
        # 获取 SettingsService 并清理缓存
        SettingsService = _get_settings_service()
        SettingsService.clear_cache()
        logger.info("缓存清理任务执行完成")
