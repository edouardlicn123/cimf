"""
================================================================================
文件：base.py
路径：/home/edo/cimf-v2/core/services/tasks/base.py
================================================================================

功能说明：
    定时任务基类，定义所有定时任务的通用接口和行为。

    主要功能：
    - 定义任务抽象接口（必须实现 execute 方法）
    - 管理任务执行状态（启用/禁用、运行次数、上次运行时间等）
    - 从系统设置读取任务配置
    - 提供任务状态查询和切换功能

版本：
    - 1.0: 从 Flask 迁移

依赖：
    - abc: 抽象基类
    - datetime: 时间处理
    - core.services.settings_service: 系统设置服务
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from django.utils.timezone import now

logger = logging.getLogger(__name__)


class CronTask(ABC):
    """
    定时任务抽象基类

    属性：
        name: str - 任务唯一标识名称
        default_interval: int - 默认执行间隔（秒）
        enabled_by_default: bool - 默认启用状态

    内部属性：
        _last_run: Optional[datetime] - 上次执行时间
        _last_status: str - 上次执行状态 ('never', 'success', 'failed')
        _last_error: Optional[str] - 上次错误信息
        _run_count: int - 执行次数
        _app_ready: bool - 应用是否就绪

    方法：
        set_app_ready(ready): 设置应用就绪状态
        is_enabled(): 检查任务是否启用
        get_interval(): 获取执行间隔
        execute(): 执行任务逻辑（抽象方法，需子类实现）
        run(): 运行任务（包含异常处理）
        get_next_run_time(): 获取下次执行时间
        get_status(): 获取任务状态
        toggle(enabled): 切换任务启用状态
    """

    name: str = "task"
    """任务唯一标识名称"""

    default_interval: int = 60
    """默认执行间隔（秒）"""

    enabled_by_default: bool = True
    """默认启用状态"""

    def __init__(self):
        """
        初始化任务状态
        """
        self._last_run: datetime | None = None
        self._last_status: str = 'never'
        self._last_error: str | None = None
        self._run_count: int = 0
        self._app_ready: bool = False

    def set_app_ready(self, ready: bool = True):
        """
        设置应用是否就绪

        参数：
            ready: 是否就绪
        """
        self._app_ready = ready

    @property
    @abstractmethod
    def setting_key_enabled(self) -> str:
        """获取启用设置项的 key"""

    @property
    @abstractmethod
    def setting_key_interval(self) -> str:
        """获取间隔设置项的 key"""

    def is_enabled(self) -> bool:
        """检查任务是否启用"""
        if not self._app_ready:
            logger.debug(f"任务 {self.name} 跳过：应用未就绪")
            return False

        try:
            from core.services import SettingsService  # noqa: PLC0415
            setting = SettingsService.get_setting(self.setting_key_enabled)
            return setting is None or setting is True or str(setting).lower() == 'true'
        except Exception as e:
            logger.warning(f"任务 {self.name} 检查启用状态失败: {e}")
            return self.enabled_by_default

    def get_interval(self) -> int:
        """获取执行间隔（秒）"""
        if not self._app_ready:
            return self.default_interval

        try:
            from core.services import SettingsService  # noqa: PLC0415
            interval = SettingsService.get_setting(self.setting_key_interval)
            if interval:
                try:
                    return int(interval)
                except (TypeError, ValueError):
                    pass
        except Exception as e:
            logger.warning(f"任务 {self.name} 获取间隔失败: {e}")
        return self.default_interval

    @abstractmethod
    def execute(self):
        """执行任务逻辑（抽象方法）"""

    def run(self):
        """运行任务（包含异常处理）"""
        if not self._app_ready:
            logger.debug(f"任务 {self.name} 跳过：应用未就绪")
            return

        if not self.is_enabled():
            return

        try:
            self.execute()
            self._last_status = 'success'
            self._last_error = None
        except Exception as e:
            self._last_status = 'failed'
            self._last_error = str(e)
            logger.error(f"任务 {self.name} 执行失败: {e}", exc_info=True)
        finally:
            self._last_run = now()
            self._run_count += 1

    def get_next_run_time(self):
        """获取下次执行时间"""
        if self._last_run:
            return self._last_run + timedelta(seconds=self.get_interval())
        return now() if self.is_enabled() else None

    def get_status(self) -> dict:
        """获取任务状态"""
        next_run = self.get_next_run_time()
        return {
            'name': self.name,
            'enabled': self.is_enabled(),
            'interval': self.get_interval(),
            'app_ready': self._app_ready,
            'last_run': self._last_run.strftime('%Y-%m-%d %H:%M:%S') if self._last_run else None,
            'next_run': next_run.strftime('%Y-%m-%d %H:%M:%S') if next_run else None,
            'last_status': self._last_status,
            'last_error': self._last_error,
            'run_count': self._run_count,
        }

    def toggle(self, enabled: bool) -> bool:
        """切换任务启用状态"""
        try:
            from core.services import SettingsService  # noqa: PLC0415
            SettingsService.save_setting(self.setting_key_enabled, enabled)
            logger.info(f"任务 {self.name} 已{'启用' if enabled else '禁用'}")
            return True
        except Exception as e:
            logger.error(f"任务 {self.name} 切换状态失败: {e}")
            return False
