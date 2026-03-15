# 文件路径：app/services/core/cron_service.py
# 功能说明：统一的定时任务调度服务
# 版本：1.2
# 创建日期：2026-03-14
# 更新日期：2026-03-15

import time
import logging
import threading
from typing import Optional, Dict, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


def handle_app_context(func: Callable) -> Callable:
    """装饰器：在 Flask app context 中执行函数"""
    def wrapper(self, *args, **kwargs):
        if not self._app:
            return {'success': False, 'error': '应用未初始化'}
        with self._app.app_context():
            return func(self, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


class CronService:
    """统一的定时任务调度服务"""

    def __init__(self, app=None):
        self._tasks: Dict = {}
        self._running: bool = False
        self._thread: Optional[threading.Thread] = None
        self._start_time: Optional[datetime] = None
        self._app = app

    def init_app(self, app):
        """初始化 Flask 应用"""
        self._app = app

    def register(self, task):
        """注册任务"""
        self._tasks[task.name] = task
        logger.info(f"任务已注册: {task.name}")

    def unregister(self, task_name: str):
        """注销任务"""
        if task_name in self._tasks:
            del self._tasks[task_name]
            logger.info(f"任务已注销: {task_name}")

    def get_task(self, task_name: str):
        """获取任务"""
        return self._tasks.get(task_name)

    def _run_loop(self):
        """调度循环"""
        logger.info("Cron 服务已启动，等待应用就绪...")
        
        # 等待应用就绪
        while self._running and not self._app:
            time.sleep(1)
        
        logger.info("Cron 服务开始执行任务")

        while self._running:
            try:
                now = time.time()
                tasks_to_run = list(self._tasks.values())

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
                    except Exception as task_error:
                        logger.error(f"任务 {task.name} 执行异常: {task_error}", exc_info=True)

            except Exception as e:
                logger.error(f"Cron 调度循环异常: {e}", exc_info=True)

            time.sleep(1)

        logger.info("Cron 服务已停止")

    def start(self):
        """启动调度器"""
        if self._running:
            logger.warning("Cron 服务已在运行中")
            return

        self._running = True
        self._start_time = datetime.now()
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
        for task in self._tasks.values():
            task.set_app_ready(ready)
        logger.info(f"Cron 任务应用就绪状态: {ready}")

    def get_status(self) -> dict:
        """获取所有任务状态"""
        return {
            'running': self._running,
            'start_time': self._start_time.strftime('%Y-%m-%d %H:%M:%S') if self._start_time else None,
            'tasks': {name: task.get_status() for name, task in self._tasks.items()},
        }

    @handle_app_context
    def trigger(self, task_name: str) -> dict:
        """手动触发任务"""
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


def get_cron_service() -> CronService:
    """获取 Cron 服务单例"""
    global _cron_service
    if _cron_service is None:
        _cron_service = CronService()
    return _cron_service
