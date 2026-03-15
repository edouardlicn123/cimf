# -*- coding: utf-8 -*-
"""
================================================================================
文件：app/services/core/cron_service.py
路径：/home/edo/cimf-v2/app/services/core/cron_service.py
================================================================================

功能说明：
    统一的定时任务调度服务，负责管理和执行后台定时任务。
    
    主要功能：
    - 注册和管理多个定时任务（Task）
    - 后台线程循环检查任务执行时间
    - 支持手动触发任务
    - 支持动态启用/禁用任务
    - 在 Flask app context 中执行任务，确保数据库访问正常

用法：
    1. 初始化：创建 CronService 实例并调用 init_app() 传入 Flask 应用
    2. 注册任务：调用 register() 方法注册 CronTask 子类实例
    3. 启动调度：调用 start() 方法启动后台调度线程
    4. 获取状态：调用 get_status() 方法获取所有任务状态
    
    示例：
        from app.services.core.cron_service import get_cron_service
        from app.services.core.tasks import TimeSyncTask, CacheCleanupTask
        
        cron = get_cron_service()
        cron.init_app(app)
        cron.register(TimeSyncTask())
        cron.register(CacheCleanupTask())
        cron.start()

版本：
    - 1.0: 初始版本，创建基础调度框架
    - 1.1: 添加装饰器处理 Flask app context
    - 1.2: 优化调度循环，空闲时减少检查频率

依赖：
    - threading: 后台线程
    - CronTask: 任务基类
    - Flask app context: 确保任务中可访问数据库
"""

import time
import logging
import threading
from typing import Optional, Dict, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# 装饰器定义
# =============================================================================

def handle_app_context(func: Callable) -> Callable:
    """
    装饰器：在 Flask app context 中执行函数
    
    说明：
        CronService 的方法可能需要在 Flask 应用上下文之外被调用
        （如 API 请求处理），此装饰器确保函数在 app.context 中执行，
        从而可以正常访问数据库等 Flask 资源。
    
    参数：
        func: 需要包装的函数
        
    返回：
        包装后的函数
    """
    def wrapper(self, *args, **kwargs):
        if not self._app:
            return {'success': False, 'error': '应用未初始化'}
        with self._app.app_context():
            return func(self, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# =============================================================================
# CronService 类
# =============================================================================

class CronService:
    """
    统一的定时任务调度服务类
    
    属性：
        _tasks: Dict[str, CronTask] - 已注册的任务字典，key 为任务名称
        _running: bool - 调度器运行状态
        _thread: Optional[threading.Thread] - 后台调度线程
        _start_time: Optional[datetime] - 调度器启动时间
        _app: Optional[Flask] - Flask 应用实例
    
    方法：
        init_app(app): 初始化 Flask 应用
        register(task): 注册任务
        unregister(task_name): 注销任务
        get_task(task_name): 获取任务实例
        start(): 启动调度器
        stop(): 停止调度器
        set_app_ready(ready): 设置任务就绪状态
        get_status(): 获取所有任务状态
        trigger(task_name): 手动触发任务
        toggle(task_name, enabled): 切换任务启用状态
    """

    def __init__(self, app=None):
        """
        初始化 CronService
        
        参数：
            app: Flask 应用实例，可选
        """
        self._tasks: Dict = {}
        self._running: bool = False
        self._thread: Optional[threading.Thread] = None
        self._start_time: Optional[datetime] = None
        self._app = app

    def init_app(self, app):
        """
        初始化 Flask 应用
        
        说明：
            在 Flask 应用创建后调用，传入应用实例以便在后台线程中使用 app context。
            必须在 start() 之前调用。
        
        参数：
            app: Flask 应用实例
        """
        self._app = app

    def register(self, task):
        """
        注册任务
        
        说明：
            将任务实例注册到调度器，注册后任务将被调度器管理。
            任务类必须继承自 CronTask 并实现 execute() 方法。
        
        参数：
            task: CronTask 子类实例
        """
        self._tasks[task.name] = task
        logger.info(f"任务已注册: {task.name}")

    def unregister(self, task_name: str):
        """
        注销任务
        
        参数：
            task_name: 任务名称
        """
        if task_name in self._tasks:
            del self._tasks[task_name]
            logger.info(f"任务已注销: {task_name}")

    def get_task(self, task_name: str):
        """
        获取任务实例
        
        参数：
            task_name: 任务名称
            
        返回：
            CronTask 实例或 None
        """
        return self._tasks.get(task_name)

    # -------------------------------------------------------------------------
    # 调度循环
    # -------------------------------------------------------------------------

    def _run_loop(self):
        """
        调度循环（内部方法）
        
        说明：
            在后台线程中运行，定期检查所有任务是否需要执行。
            - 任务首次执行（run_count=0）时立即执行
            - 根据任务的间隔时间计算下次执行时间
            - 任务执行后在 Flask app context 中运行
            - 有任务执行时间隔1秒，空闲时间隔5秒
        """
        logger.info("Cron 服务已启动，等待应用就绪...")
        
        # 等待应用就绪
        while self._running and not self._app:
            time.sleep(1)
        
        logger.info("Cron 服务开始执行任务")

        while self._running:
            try:
                now = time.time()
                tasks_to_run = list(self._tasks.values())
                any_task_ran = False

                for task in tasks_to_run:
                    try:
                        # 在 app context 中执行任务
                        with self._app.app_context():
                            if not task.is_enabled():
                                continue

                            # 使用任务属性判断，避免重复执行
                            should_run = False
                            
                            if task._last_run is None:
                                # 首次执行：只有当 run_count 为 0 时才执行
                                if task._run_count == 0:
                                    should_run = True
                            else:
                                next_run = task._last_run.timestamp() + task.get_interval()
                                if now >= next_run:
                                    should_run = True
                            
                            if should_run:
                                logger.info(f"执行任务: {task.name}, run_count={task._run_count}, last_run={task._last_run}")
                                task.run()
                                logger.info(f"任务完成: {task.name}, 状态: {task._last_status}, run_count={task._run_count}")
                                any_task_ran = True
                    except Exception as task_error:
                        logger.error(f"任务 {task.name} 执行异常: {task_error}", exc_info=True)

                # 如果有任务执行，下次检查间隔短；否则延长检查间隔
                sleep_time = 1 if any_task_ran else 5

            except Exception as e:
                logger.error(f"Cron 调度循环异常: {e}", exc_info=True)
                sleep_time = 5

            time.sleep(sleep_time)

        logger.info("Cron 服务已停止")

    # -------------------------------------------------------------------------
    # 启动/停止
    # -------------------------------------------------------------------------

    def start(self):
        """
        启动调度器
        
        说明：
            启动后台线程运行调度循环。
            必须在 init_app() 之后调用。
        """
        if self._running:
            logger.warning("Cron 服务已在运行中")
            return

        self._running = True
        self._start_time = datetime.now()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Cron 后台线程已启动")

    def stop(self):
        """
        停止调度器
        
        说明：
            优雅停止调度器，等待后台线程结束。
        """
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Cron 服务已停止")

    def set_app_ready(self, ready: bool = True):
        """
        设置所有任务应用已就绪
        
        说明：
            在应用初始化完成后调用，标记所有任务可以开始执行。
            这确保任务不会在应用完全启动前被执行。
        
        参数：
            ready: 是否就绪，默认为 True
        """
        for task in self._tasks.values():
            task.set_app_ready(ready)
        logger.info(f"Cron 任务应用就绪状态: {ready}")

    # -------------------------------------------------------------------------
    # 状态和操作
    # -------------------------------------------------------------------------

    def get_status(self) -> dict:
        """
        获取所有任务状态
        
        返回：
            包含调度器和所有任务状态的字典
        """
        return {
            'running': self._running,
            'start_time': self._start_time.strftime('%Y-%m-%d %H:%M:%S') if self._start_time else None,
            'tasks': {name: task.get_status() for name, task in self._tasks.items()},
        }

    @handle_app_context
    def trigger(self, task_name: str) -> dict:
        """
        手动触发任务
        
        说明：
            立即执行指定任务，不受调度间隔限制。
            用于管理员手动执行任务。
        
        参数：
            task_name: 任务名称
            
        返回：
            执行结果字典，包含 success、task、status、last_run 字段
        """
        task = self.get_task(task_name)
        if not task:
            return {'success': False, 'error': f'任务不存在: {task_name}'}

        if not task.is_enabled():
            return {'success': False, 'error': f'任务未启用: {task_name}'}

        task.run()

        return {
            'success': True,
            'task': task_name,
            'status': task._last_status,
            'last_run': task._last_run.strftime('%Y-%m-%d %H:%M:%S') if task._last_run else None,
        }

    @handle_app_context
    def toggle(self, task_name: str, enabled: bool) -> dict:
        """
        切换任务启用状态
        
        说明：
            动态启用或禁用任务，状态会保存到系统设置中。
        
        参数：
            task_name: 任务名称
            enabled: 是否启用
            
        返回：
            操作结果字典
        """
        task = self.get_task(task_name)
        if not task:
            return {'success': False, 'error': f'任务不存在: {task_name}'}

        success = task.toggle(enabled)

        return {
            'success': success,
            'task': task_name,
            'enabled': enabled,
        }


# =============================================================================
# 单例模式
# =============================================================================

_cron_service: Optional[CronService] = None


def get_cron_service() -> CronService:
    """
    获取 Cron 服务单例
    
    说明：
        使用单例模式确保整个应用只有一个 CronService 实例。
    
    返回：
        CronService 实例
    """
    global _cron_service
    if _cron_service is None:
        _cron_service = CronService()
    return _cron_service
