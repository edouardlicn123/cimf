# -*- coding: utf-8 -*-
"""
================================================================================
文件：app/services/core/tasks/__init__.py
路径：/home/edo/cimf-v2/app/services/core/tasks/__init__.py
================================================================================

功能说明：
    定时任务模块初始化文件，统一导出所有任务类。
    
    此模块作为任务模块的统一入口，方便其他模块导入任务类。
    
导出内容：
    - CronTask: 任务基类
    - TimeSyncTask: 时间同步任务
    - CacheCleanupTask: 缓存清理任务

用法：
    from app.services.core.tasks import TimeSyncTask, CacheCleanupTask
    
版本：
    - 1.0: 初始版本
"""

# 任务基类
from app.services.core.tasks.base import CronTask

# 具体任务实现
from app.services.core.tasks.time_sync_task import TimeSyncTask
from app.services.core.tasks.cache_cleanup_task import CacheCleanupTask

# 模块导出清单
__all__ = ['CronTask', 'TimeSyncTask', 'CacheCleanupTask']
