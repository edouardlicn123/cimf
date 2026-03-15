# -*- coding: utf-8 -*-
"""
================================================================================
文件：app/services/core/tasks/base.py
路径：/home/edo/cimf-v2/app/services/core/tasks/base.py
================================================================================

功能说明：
    定时任务基类，定义所有定时任务的通用接口和行为。
    
    主要功能：
    - 定义任务抽象接口（必须实现 execute 方法）
    - 管理任务执行状态（启用/禁用、运行次数、上次运行时间等）
    - 从系统设置读取任务配置
    - 提供任务状态查询和切换功能

用法：
    1. 创建任务类：继承 CronTask 并实现 execute() 方法
    2. 配置属性：设置 name、default_interval、setting_key_enabled 等属性
    3. 注册任务：将实例注册到 CronService
    4. 调度执行：由 CronService 自动调度执行
    
    示例：
        class MyTask(CronTask):
            name = "my_task"
            default_interval = 3600  # 1小时
            
            @property
            def setting_key_enabled(self):
                return "my_task_enabled"
                
            @property
            def setting_key_interval(self):
                return "my_task_interval"
                
            def execute(self):
                # 执行具体任务逻辑
                pass

版本：
    - 1.0: 初始版本
    - 1.1: 优化导入方式，添加下次执行时间计算

依赖：
    - abc: 抽象基类
    - datetime: 时间处理
    - SettingsService: 系统设置服务
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# 模块级函数
# =============================================================================

# 模块级别导入，避免重复导入，提高性能
_settings_service = None


def _get_settings_service():
    """
    获取 SettingsService 类（延迟加载）
    
    说明：
        使用延迟加载避免循环导入问题，同时确保 SettingsService
        只被导入一次，提高性能。
    
    返回：
        SettingsService 类
    """
    global _settings_service
    if _settings_service is None:
        from app.services.core.settings_service import SettingsService
        _settings_service = SettingsService
    return _settings_service


# =============================================================================
# CronTask 抽象基类
# =============================================================================

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
        self._last_run: Optional[datetime] = None
        self._last_status: str = 'never'
        self._last_error: Optional[str] = None
        self._run_count: int = 0
        self._app_ready: bool = False

    def set_app_ready(self, ready: bool = True):
        """
        设置应用是否就绪
        
        说明：
            在 Flask 应用完全初始化后调用，确保任务可以安全访问数据库等资源。
        
        参数：
            ready: 是否就绪
        """
        self._app_ready = ready

    # -------------------------------------------------------------------------
    # 抽象属性（子类必须实现）
    # -------------------------------------------------------------------------

    @property
    @abstractmethod
    def setting_key_enabled(self) -> str:
        """
        获取启用设置项的 key
        
        说明：
            子类必须实现此属性，返回系统设置中控制任务启用状态的 key。
            例如：'cron_cache_cleanup_enabled'
        
        返回：
            设置项 key 字符串
        """
        pass

    @property
    @abstractmethod
    def setting_key_interval(self) -> str:
        """
        获取间隔设置项的 key
        
        说明：
            子类必须实现此属性，返回系统设置中控制任务执行间隔的 key。
            例如：'cron_cache_cleanup_interval'
        
        返回：
            设置项 key 字符串
        """
        pass

    # -------------------------------------------------------------------------
    # 状态查询
    # -------------------------------------------------------------------------

    def is_enabled(self) -> bool:
        """
        检查任务是否启用
        
        说明：
            从系统设置中读取任务的启用状态。
            如果应用未就绪，返回 False。
            如果读取设置失败，返回 enabled_by_default 作为默认值。
        
        返回：
            True 表示任务已启用，False 表示未启用
        """
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
        """
        获取执行间隔（秒）
        
        说明：
            从系统设置中读取任务的执行间隔。
            如果应用未就绪或读取失败，返回默认值。
        
        返回：
            执行间隔秒数
        """
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

    # -------------------------------------------------------------------------
    # 任务执行
    # -------------------------------------------------------------------------

    @abstractmethod
    def execute(self):
        """
        执行任务逻辑（抽象方法）
        
        说明：
            子类必须实现此方法，定义任务的具体执行逻辑。
            此方法中不应处理异常，由 run() 方法统一处理。
        """
        pass

    def run(self):
        """
        运行任务（包含异常处理）
        
        说明：
            调度器调用的入口方法，包含完整的异常处理逻辑。
            流程：
            1. 检查应用是否就绪
            2. 检查任务是否启用
            3. 调用 execute() 执行任务
            4. 记录执行状态和结果
            5. 更新最后执行时间和次数
        """
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

    # -------------------------------------------------------------------------
    # 状态查询
    # -------------------------------------------------------------------------

    def get_next_run_time(self) -> Optional[datetime]:
        """
        获取下次执行时间
        
        说明：
            根据上次执行时间和间隔计算下次执行时间。
            如果任务未启用，返回 None。
        
        返回：
            datetime 对象或 None
        """
        if self._last_run:
            return self._last_run + timedelta(seconds=self.get_interval())
        return datetime.now() if self.is_enabled() else None

    def get_status(self) -> dict:
        """
        获取任务状态
        
        说明：
            返回任务的完整状态信息，用于 API 展示和调试。
        
        返回：
            包含任务所有状态信息的字典
        """
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

    # -------------------------------------------------------------------------
    # 任务管理
    # -------------------------------------------------------------------------

    def toggle(self, enabled: bool) -> bool:
        """
        切换任务启用状态
        
        说明：
            修改任务的启用状态，并保存到系统设置中。
        
        参数：
            enabled: 是否启用任务
            
        返回：
            操作是否成功
        """
        try:
            SettingsService = _get_settings_service()
            SettingsService.save_setting(self.setting_key_enabled, enabled)
            logger.info(f"任务 {self.name} 已{'启用' if enabled else '禁用'}")
            return True
        except Exception as e:
            logger.error(f"任务 {self.name} 切换状态失败: {e}")
            return False
