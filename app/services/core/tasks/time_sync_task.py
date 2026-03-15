# -*- coding: utf-8 -*-
"""
================================================================================
文件：app/services/core/tasks/time_sync_task.py
路径：/home/edo/cimf-v2/app/services/core/tasks/time_sync_task.py
================================================================================

功能说明：
    时间同步任务，定时与远程时间服务器同步系统时间。
    
    主要功能：
    - 调用 TimeSyncService 同步时间
    - 可配置同步间隔（默认15分钟）
    - 从系统设置读取配置
    
    此任务是 CronService 管理的具体任务实现之一。

用法：
    1. 注册到 CronService：
        from app.services.core.cron_service import get_cron_service
        from app.services.core.tasks import TimeSyncTask
        cron = get_cron_service()
        cron.register(TimeSyncTask())
    
    2. 通过系统设置配置：
        - enable_time_sync: 是否启用（默认 true）
        - time_sync_interval: 同步间隔分钟数（默认 15）

版本：
    - 1.0: 初始版本
    - 1.1: 优化导入方式

依赖：
    - CronTask: 任务基类
    - TimeSyncService: 时间同步服务
"""

from app.services.core.tasks.base import CronTask, _get_settings_service
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# TimeSyncTask 类
# =============================================================================

class TimeSyncTask(CronTask):
    """
    时间同步任务类
    
    说明：
        定时与远程时间服务器同步系统时间，确保系统时间的准确性。
        实际同步逻辑由 TimeSyncService 完成，此任务作为调度层。
    """

    # 任务名称
    name = "time_sync"
    
    # 默认执行间隔：15分钟（900秒）
    default_interval = 900

    @property
    def setting_key_enabled(self) -> str:
        """
        获取启用设置项的 key
        
        返回：
            'enable_time_sync'
        """
        return "enable_time_sync"

    @property
    def setting_key_interval(self) -> str:
        """
        获取间隔设置项的 key
        
        返回：
            'time_sync_interval'
        """
        return "time_sync_interval"

    def get_interval(self) -> int:
        """
        获取执行间隔（秒）
        
        说明：
            重写父类方法，因为系统设置中存储的是分钟数，
            需要转换为秒数。
        
        返回：
            执行间隔秒数
        """
        try:
            SettingsService = _get_settings_service()
            interval = SettingsService.get_setting(self.setting_key_interval)
            if interval and isinstance(interval, int):
                return interval * 60  # 分钟转换为秒
        except Exception as e:
            logger.warning(f"获取时间同步间隔失败: {e}")
        return self.default_interval

    def execute(self):
        """
        执行时间同步
        
        说明：
            调用 TimeSyncService 完成实际的时间同步逻辑。
        """
        from app.services.core.time_sync_service import get_time_sync_service
        time_sync = get_time_sync_service()
        time_sync.sync_time()
