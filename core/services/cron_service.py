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

import logging
import os
import threading
import time
from importlib import import_module
from typing import TYPE_CHECKING

from django.utils.timezone import now

from core.services.mixins import SingletonMixin, error_response, success_response

if TYPE_CHECKING:
    from datetime import datetime

logger = logging.getLogger(__name__)


class CronService(SingletonMixin):
    """
    统一的定时任务调度服务类

    属性：
        _tasks: Dict[str, CronTask] - 已注册的任务字典
        _running: bool - 调度器运行状态
        _thread: Optional[threading.Thread] - 后台调度线程
        _start_time: Optional[datetime] - 调度器启动时间
    """

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._tasks: dict = {}
        self._lock: threading.Lock = threading.Lock()
        self._running: bool = False
        self._thread: threading.Thread | None = None
        self._start_time: datetime | None = None
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

    def _should_run(self, task):
        """判断任务是否需要执行"""
        if not task.is_enabled():
            return False
        if task._last_run is None:
            return task._run_count == 0
        next_run = task._last_run.timestamp() + task.get_interval()
        return time.time() >= next_run

    def _execute_task(self, task):
        """执行单个任务"""
        try:
            logger.info(f"执行任务: {task.name}, run_count={task._run_count}, last_run={task._last_run}")
            task.run()
            logger.info(f"任务完成: {task.name}, 状态: {task._last_status}, run_count={task._run_count}")
            return True
        except Exception as e:
            logger.error(f"任务 {task.name} 执行失败: {e}", exc_info=True)
            return False

    def _run_loop(self):
        """调度循环（内部方法）"""
        logger.info("Cron 服务已启动，等待应用就绪...")

        time.sleep(10)

        logger.info("Cron 服务开始执行任务")

        while self._running:
            sleep_time = 5
            try:
                tasks_to_run = list(self._tasks.values())
                any_task_ran = False

                for task in tasks_to_run:
                    try:
                        if self._should_run(task):
                            any_task_ran = self._execute_task(task) or any_task_ran
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
            "running": self._running,
            "start_time": self._start_time.strftime("%Y-%m-%d %H:%M:%S") if self._start_time else None,
            "tasks": {name: task.get_status() for name, task in tasks_snapshot.items()},
        }

    def trigger(self, task_name: str) -> dict:
        """手动触发任务"""
        task = self.get_task(task_name)
        if not task:
            return error_response(f"任务不存在: {task_name}")

        if not task.is_enabled():
            return error_response(f"任务未启用: {task_name}")

        try:
            task.run()
        except Exception as e:
            logger.error(f"手动触发任务 {task_name} 失败: {e}", exc_info=True)
            return error_response(f"任务执行失败: {e!s}")

        return success_response(
            task=task_name,
            status=task._last_status,
            last_run=task._last_run.strftime("%Y-%m-%d %H:%M:%S") if task._last_run else None,
        )

    def toggle(self, task_name: str, enabled: bool) -> dict:
        """切换任务启用状态"""
        task = self.get_task(task_name)
        if not task:
            return error_response(f"任务不存在: {task_name}")

        success = task.toggle(enabled)

        return success_response(success=success, task=task_name, enabled=enabled)


def get_cron_service() -> CronService:
    """获取 Cron 服务单例"""
    return CronService()


def _register_single_task(task_path: str):
    """按完整导入路径注册单个 cron 任务"""
    mod_path, cls_name = task_path.rsplit(".", 1)
    task_class = getattr(import_module(mod_path), cls_name)
    task = task_class()
    get_cron_service().register(task)
    logger.info(f"Cron 任务已注册: {task.name} ({task_path})")


def _unregister_single_task(task_path: str):
    """按完整导入路径注销单个 cron 任务"""
    mod_path, cls_name = task_path.rsplit(".", 1)
    task_class = getattr(import_module(mod_path), cls_name)
    get_cron_service().unregister(task_class.name)
    logger.info(f"Cron 任务已注销: {task_class.name} ({task_path})")


def _register_installed_module_tasks():
    """扫描所有已安装且激活的模块，注册其 cron_tasks"""
    from core.module.models import Module  # noqa: PLC0415
    from core.module.services.module_service import ModuleService  # noqa: PLC0415

    for mod in Module.objects.filter(is_installed=True, is_active=True):
        info = ModuleService.load_module_info(mod.path) or {}
        for task_path in info.get("cron_tasks", []):
            try:
                _register_single_task(task_path)
            except Exception as e:
                logger.warning(f"模块 {mod.module_id} cron 任务注册失败: {e}")


def init_cron_service():
    """初始化 Cron 服务并注册任务"""

    # 防止重复初始化（Django autoreload 会创建子进程，每个进程都会调用 ready()）
    # 使用环境变量标记，在子进程中不初始化 cron 服务
    if os.environ.get("CIMF_CRON_INITIALIZED"):
        return
    os.environ["CIMF_CRON_INITIALIZED"] = "1"

    from core.services.tasks import CacheCleanupTask, EmailCleanupTask, EmailSendingTask, TimeSyncTask  # noqa: PLC0415

    cron = get_cron_service()

    # 防止重复注册
    if cron._tasks:
        logger.info("Cron 服务已注册任务，跳过")
        return

    cron.register(TimeSyncTask())
    cron.register(CacheCleanupTask())
    cron.register(EmailSendingTask())
    cron.register(EmailCleanupTask())
    _register_installed_module_tasks()
    cron.set_app_ready(True)
    cron.start()
    logger.info("Cron 服务初始化完成")
