# -*- coding: utf-8 -*-
"""
================================================================================
文件：cron_service.py
路径：/home/edo/cimf-v2/core/services/cron_service.py
================================================================================

功能说明：
    统一的定时任务调度服务，负责管理和执行后台定时任务。
    
    主要功能：
    - 注册和管理多个定时任务（Task）
    - 后台线程循环检查任务执行时间
    - 支持手动触发任务
    - 支持动态启用/禁用任务
    - 在 Django app context 中执行任务，确保数据库访问正常

版本：
    - 1.0: 从 Flask 迁移

依赖：
    - threading: 后台线程
    - CronTask: 任务基类
"""

import time
import logging
import threading
from datetime import datetime
from typing import Optional, Dict
from django.utils.timezone import now

logger = logging.getLogger(__name__)


class CronService:
    """
    统一的定时任务调度服务类
    
    属性：
        _tasks: Dict[str, CronTask] - 已注册的任务字典
        _running: bool - 调度器运行状态
        _thread: Optional[threading.Thread] - 后台调度线程
        _start_time: Optional[datetime] - 调度器启动时间
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._tasks: Dict = {}
        self._lock: threading.Lock = threading.Lock()
        self._running: bool = False
        self._thread: Optional[threading.Thread] = None
        self._start_time: Optional[datetime] = None
        self._initialized = True

    def register(self, task):
        """注册任务"""
        with self._lock:
            self._tasks[task.name] = task
        logger.info(f"任务已注册: {task.name}")

    def unregister(self, task_name: str):
        """注销任务"""
        with self._lock:
            self._tasks.pop(task_name, None)
        logger.info(f"任务已注销: {task_name}")

    def get_task(self, task_name: str):
        """获取任务实例"""
        with self._lock:
            return self._tasks.get(task_name)

    def _run_loop(self):
        """调度循环（内部方法）"""
        logger.info("Cron 服务已启动，等待应用就绪...")
        
        time.sleep(10)
        
        logger.info("Cron 服务开始执行任务")

        while self._running:
            sleep_time = 5
            try:
                now = time.time()
                tasks_to_run = list(self._tasks.values())
                any_task_ran = False

                for task in tasks_to_run:
                    try:
                        if not task.is_enabled():
                            continue
                        
                        should_run = False
                        
                        if task._last_run is None:
                            if task._run_count == 0:
                                should_run = True
                        else:
                            next_run = task._last_run.timestamp() + task.get_interval()
                            if now >= next_run:
                                should_run = True
                        
                        if should_run:
                            logger.info(f"执行任务: {task.name}, run_count={task._run_count}, last_run={task._last_run}")
                            try:
                                task.run()
                                logger.info(f"任务完成: {task.name}, 状态: {task._last_status}, run_count={task._run_count}")
                            except Exception as run_error:
                                logger.error(f"任务 {task.name} 执行失败: {run_error}", exc_info=True)
                            any_task_ran = True
                    except Exception as task_error:
                        logger.error(f"任务 {task.name} 执行异常: {task_error}", exc_info=True)

                sleep_time = 1 if any_task_ran else 5

            except Exception as e:
                logger.error(f"Cron 调度循环异常: {e}", exc_info=True)
                sleep_time = 5

            time.sleep(sleep_time)

        logger.info("Cron 服务已停止")

    _app_ready: bool = False

    def start(self):
        """启动调度器"""
        if self._running:
            logger.warning("Cron 服务已在运行中")
            return

        self._running = True
        self._start_time = now()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Cron 后台线程已启动")

    def stop(self):
        """停止调度器"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Cron 服务已停止")

    def set_app_ready(self, ready: bool = True):
        """设置所有任务应用已就绪"""
        self._app_ready = ready
        for task in self._tasks.values():
            task.set_app_ready(ready)
        logger.info(f"Cron 任务应用就绪状态: {ready}")

    def get_status(self) -> dict:
        """获取所有任务状态"""
        with self._lock:
            tasks_snapshot = dict(self._tasks)
        return {
            'running': self._running,
            'start_time': self._start_time.strftime('%Y-%m-%d %H:%M:%S') if self._start_time else None,
            'tasks': {name: task.get_status() for name, task in tasks_snapshot.items()},
        }

    def trigger(self, task_name: str) -> dict:
        """手动触发任务"""
        task = self.get_task(task_name)
        if not task:
            return {'success': False, 'error': f'任务不存在: {task_name}'}

        if not task.is_enabled():
            return {'success': False, 'error': f'任务未启用: {task_name}'}

        try:
            task.run()
        except Exception as e:
            logger.error(f"手动触发任务 {task_name} 失败: {e}", exc_info=True)
            return {'success': False, 'error': f'任务执行失败: {str(e)}'}

        return {
            'success': True,
            'task': task_name,
            'status': task._last_status,
            'last_run': task._last_run.strftime('%Y-%m-%d %H:%M:%S') if task._last_run else None,
        }

    def toggle(self, task_name: str, enabled: bool) -> dict:
        """切换任务启用状态"""
        task = self.get_task(task_name)
        if not task:
            return {'success': False, 'error': f'任务不存在: {task_name}'}

        success = task.toggle(enabled)

        return {
            'success': success,
            'task': task_name,
            'enabled': enabled,
        }


_cron_service: Optional[CronService] = None
_cron_initialized: bool = False


def get_cron_service() -> CronService:
    """获取 Cron 服务单例"""
    global _cron_service
    if _cron_service is None:
        _cron_service = CronService()
    return _cron_service


def init_cron_service():
    """初始化 Cron 服务并注册任务"""
    global _cron_initialized
    
    # 防止重复初始化（Django autoreload 会创建子进程，每个进程都会调用 ready()）
    # 使用环境变量标记，在子进程中不初始化 cron 服务
    import os
    if os.environ.get('CIMF_CRON_INITIALIZED'):
        return
    os.environ['CIMF_CRON_INITIALIZED'] = '1'
    
    from core.services.tasks import TimeSyncTask, CacheCleanupTask, EmailSendingTask, EmailCleanupTask
    
    cron = get_cron_service()
    
    # 防止重复注册
    if cron._tasks:
        logger.info("Cron 服务已注册任务，跳过")
        return
    
    cron.register(TimeSyncTask())
    cron.register(CacheCleanupTask())
    cron.register(EmailSendingTask())
    cron.register(EmailCleanupTask())
    cron.set_app_ready(True)
    cron.start()
    logger.info("Cron 服务初始化完成")
