# -*- coding: utf-8 -*-
"""
================================================================================
文件：app/services/core/time_sync_service.py
路径：/home/edo/cimf-v2/app/services/core/time_sync_service.py
================================================================================

功能说明：
    时钟同步服务，负责与远程时间服务器同步系统时间。
    
    主要功能：
    - 从远程时间服务器获取准确时间
    - 支持多个时间服务器（主服务器 + 备份服务器）
    - 支持失败重试机制
    - 失败时返回本地时间作为备选
    
    设计说明：
    - 此服务不直接管理调度，由 CronService 的 TimeSyncTask 调用
    - 同步成功后，会持续返回同步后的时间加上流逝时间
    - 如果从未同步成功，返回本地时间

用法：
    1. 获取服务实例：
        from app.services.core.time_sync_service import get_time_sync_service
        time_sync = get_time_sync_service()
    
    2. 执行同步：
        success = time_sync.sync_time()
    
    3. 获取当前时间：
        now = time_sync.get_current_time()
    
    4. 获取状态：
        status = time_sync.get_status()

版本：
    - 1.0: 初始版本
    - 1.1: 优化导入方式
    - 1.2: 使用模块级 lazy loading

依赖：
    - urllib.request: 网络请求
    - json: JSON 解析
    - SettingsService: 系统设置服务
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Optional
from urllib.request import urlopen
import json

logger = logging.getLogger(__name__)


# =============================================================================
# 模块级函数
# =============================================================================

# 模块级别导入，避免重复导入
_settings_service = None


def _get_settings_service():
    """
    获取 SettingsService 类（延迟加载）
    
    说明：
        使用延迟加载避免循环导入问题。
    
    返回：
        SettingsService 类
    """
    global _settings_service
    if _settings_service is None:
        from app.services.core.settings_service import SettingsService
        _settings_service = SettingsService
    return _settings_service


# =============================================================================
# TimeSyncService 类
# =============================================================================

class TimeSyncService:
    """
    时钟同步服务类
    
    说明：
        负责与远程时间服务器同步时间，提供统一的时间获取接口。
        由 CronService 调度执行同步任务。
    
    类属性：
        DEFAULT_SYNC_INTERVAL: int - 默认同步间隔（秒）
        DEFAULT_MAX_RETRIES: int - 默认最大重试次数
        DEFAULT_RETRY_DELAY: int - 重试间隔（秒）
        DEFAULT_SERVER_URL: str - 默认时间服务器 URL
        BACKUP_SERVERS: list - 备份时间服务器列表
    
    实例属性：
        _synced_time: Optional[datetime] - 上次同步成功的服务器时间
        _last_sync_timestamp: Optional[float] - 上次同步的时间戳
        _sync_status: str - 同步状态 ('never', 'success', 'failed')
    """

    # 默认配置
    DEFAULT_SYNC_INTERVAL = 15 * 60  # 15分钟
    DEFAULT_MAX_RETRIES = 5           # 最多重试5次
    DEFAULT_RETRY_DELAY = 2            # 重试间隔2秒
    DEFAULT_SERVER_URL = 'https://api.uuni.cn/api/time'

    # 备用服务器列表
    BACKUP_SERVERS = [
        'https://api.uuni.cn/api/time',
        'http://api.baidu.com/time/get',
        'http://worldtimeapi.org/api/timezone/Asia/Shanghai',
    ]

    def __init__(self):
        """
        初始化时间同步服务
        """
        self._synced_time: Optional[datetime] = None
        self._last_sync_timestamp: Optional[float] = None
        self._sync_status: str = 'never'

    # -------------------------------------------------------------------------
    # 配置读取
    # -------------------------------------------------------------------------

    def is_enabled(self) -> bool:
        """
        检查时间同步是否启用
        
        返回：
            是否启用
        """
        SettingsService = _get_settings_service()
        setting = SettingsService.get_setting('enable_time_sync')
        return setting is None or setting is True or setting == 'true'

    def get_sync_interval(self) -> int:
        """
        获取同步间隔（秒）
        
        说明：
            从系统设置读取，转换为秒。
        
        返回：
            同步间隔秒数
        """
        SettingsService = _get_settings_service()
        interval = SettingsService.get_setting('time_sync_interval')
        if interval and isinstance(interval, int):
            return interval * 60
        return self.DEFAULT_SYNC_INTERVAL

    def get_max_retries(self) -> int:
        """
        获取最大重试次数
        
        返回：
            重试次数
        """
        SettingsService = _get_settings_service()
        retries = SettingsService.get_setting('time_sync_max_retries')
        if retries and isinstance(retries, int):
            return retries
        return self.DEFAULT_MAX_RETRIES

    def get_server_url(self) -> str:
        """
        获取时间服务器 URL
        
        返回：
            服务器 URL 字符串
        """
        SettingsService = _get_settings_service()
        url = SettingsService.get_setting('time_server_url')
        return url or self.DEFAULT_SERVER_URL

    # -------------------------------------------------------------------------
    # 时间同步
    # -------------------------------------------------------------------------

    def _fetch_time_from_server(self, url: str) -> Optional[datetime]:
        """
        从指定服务器获取时间（内部方法）
        
        说明：
            向时间服务器发送请求，解析返回的时间数据。
            支持多种 API 格式：
            - {date: '2024-01-01 12:00:00'}
            - {datetime: '2024-01-01T12:00:00+08:00'}
        
        参数：
            url: 时间服务器 URL
            
        返回：
            datetime 对象或 None（失败时）
        """
        try:
            with urlopen(url, timeout=3) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    # 尝试从不同字段获取时间
                    date_str = data.get('date') or data.get('datetime', '').split('+')[0]
                    if date_str:
                        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.warning(f"从 {url} 获取时间失败: {e}")
        return None

    def _try_sync_with_servers(self) -> bool:
        """
        尝试从服务器同步时间（内部方法）
        
        说明：
            按顺序尝试主服务器和备份服务器，
            如果失败则重试直到达到最大次数。
        
        返回：
            是否同步成功
        """
        # 构建服务器列表（去除重复）
        servers = [self.get_server_url()] + self.BACKUP_SERVERS
        servers = list(dict.fromkeys(servers))
        max_retries = self.get_max_retries()

        for attempt in range(max_retries):
            for server_url in servers:
                logger.info(f"尝试从 {server_url} 同步时间 (尝试 {attempt + 1}/{max_retries})")
                server_time = self._fetch_time_from_server(server_url)
                if server_time:
                    self._synced_time = server_time
                    self._last_sync_timestamp = time.time()
                    self._sync_status = 'success'
                    logger.info(f"时间同步成功: {server_time}")
                    return True

            # 重试前等待
            if attempt < max_retries - 1:
                logger.info(f"所有服务器同步失败，{self.DEFAULT_RETRY_DELAY}秒后重试...")
                time.sleep(self.DEFAULT_RETRY_DELAY)

        self._sync_status = 'failed'
        logger.error("时间同步失败，已达到最大重试次数")
        return False

    def sync_time(self) -> bool:
        """
        执行时间同步
        
        说明：
            由 CronService 的 TimeSyncTask 调用。
            如果同步未启用，直接返回 False。
        
        返回：
            是否同步成功
        """
        if not self.is_enabled():
            logger.info("时间同步已禁用")
            return False
        return self._try_sync_with_servers()

    # -------------------------------------------------------------------------
    # 时间获取
    # -------------------------------------------------------------------------

    def get_current_time(self) -> datetime:
        """
        获取当前时间
        
        说明：
            如果同步成功，返回同步时间加上流逝时间。
            如果从未同步或同步失败，返回本地时间。
        
        返回：
            datetime 对象
        """
        if (self._synced_time is not None and
            self._sync_status == 'success' and
            self._last_sync_timestamp is not None):
            elapsed = time.time() - self._last_sync_timestamp
            return self._synced_time + timedelta(seconds=elapsed)
        return datetime.now()

    def get_current_time_str(self, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
        """
        获取当前时间字符串
        
        参数：
            fmt: 时间格式字符串
            
        返回：
            格式化的时间字符串
        """
        return self.get_current_time().strftime(fmt)

    # -------------------------------------------------------------------------
    # 状态查询
    # -------------------------------------------------------------------------

    def get_status(self) -> dict:
        """
        获取同步状态
        
        返回：
            包含状态信息的字典
        """
        return {
            'status': self._sync_status,
            'synced_time': self._synced_time.strftime('%Y-%m-%d %H:%M:%S') if self._synced_time else None,
            'last_sync_timestamp': self._last_sync_timestamp,
            'enabled': self.is_enabled(),
        }


# =============================================================================
# 单例模式
# =============================================================================

_time_sync_service: Optional[TimeSyncService] = None


def get_time_sync_service() -> TimeSyncService:
    """
    获取时间同步服务单例
    
    返回：
        TimeSyncService 实例
    """
    global _time_sync_service
    if _time_sync_service is None:
        _time_sync_service = TimeSyncService()
    return _time_sync_service
