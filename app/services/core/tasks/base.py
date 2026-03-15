# 文件路径：app/services/core/tasks/base.py
# 功能说明：定时任务基类
# 版本：1.1
# 更新日期：2026-03-15

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# 模块级别导入，避免重复导入
_settings_service = None


def _get_settings_service():
    global _settings_service
    if _settings_service is None:
        from app.services.core.settings_service import SettingsService
        _settings_service = SettingsService
    return _settings_service


class CronTask(ABC):
    """定时任务基类"""

    name: str = "task"
    default_interval: int = 60
    enabled_by_default: bool = True

    def __init__(self):
        self._last_run: Optional[datetime] = None
        self._last_status: str = 'never'
        self._last_error: Optional[str] = None
        self._run_count: int = 0
        self._app_ready: bool = False

    def set_app_ready(self, ready: bool = True):
        """设置应用是否就绪"""
        self._app_ready = ready

    @property
    @abstractmethod
    def setting_key_enabled(self) -> str:
        """获取启用设置项的 key"""
        pass

    @property
    @abstractmethod
    def setting_key_interval(self) -> str:
        """获取间隔设置项的 key"""
        pass

    def is_enabled(self) -> bool:
        """是否启用此任务"""
        if not self._app_ready:
            logger.debug(f"任务 {self.name} 跳过：应用未就绪")
            return False
        
        try:
            SettingsService = _get_settings_service()
            setting = SettingsService.get_setting(self.setting_key_enabled)
            return setting is None or setting is True or setting == 'true'
        except Exception as e:
            logger.warning(f"任务 {self.name} 检查启用状态失败: {e}")
            return self.enabled_by_default

    def get_interval(self) -> int:
        """获取执行间隔（秒）"""
        if not self._app_ready:
            return self.default_interval
        
        try:
            SettingsService = _get_settings_service()
            interval = SettingsService.get_setting(self.setting_key_interval)
            if interval and isinstance(interval, int):
                return interval
        except Exception as e:
            logger.warning(f"任务 {self.name} 获取间隔失败: {e}")
        return self.default_interval

    @abstractmethod
    def execute(self):
        """执行任务逻辑"""
        pass

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
            self._last_run = datetime.now()
            self._run_count += 1

    def get_next_run_time(self) -> Optional[datetime]:
        """获取下次执行时间"""
        if self._last_run:
            return self._last_run + timedelta(seconds=self.get_interval())
        return datetime.now() if self.is_enabled() else None

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
            SettingsService = _get_settings_service()
            SettingsService.save_setting(self.setting_key_enabled, enabled)
            logger.info(f"任务 {self.name} 已{'启用' if enabled else '禁用'}")
            return True
        except Exception as e:
            logger.error(f"任务 {self.name} 切换状态失败: {e}")
            return False
