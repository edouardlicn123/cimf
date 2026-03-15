# 文件路径：app/services/core/time_sync_service.py
# 功能说明：时钟同步服务 - 提供时间同步逻辑（由 Cron 服务调度）
# 版本：1.1
# 创建日期：2026-03-14

import time
import logging
from datetime import datetime, timedelta
from typing import Optional
from urllib.request import urlopen
import json

logger = logging.getLogger(__name__)


class TimeSyncService:
    """时钟同步服务"""

    DEFAULT_SYNC_INTERVAL = 15 * 60
    DEFAULT_MAX_RETRIES = 5
    DEFAULT_RETRY_DELAY = 2
    DEFAULT_SERVER_URL = 'https://api.uuni.cn/api/time'

    BACKUP_SERVERS = [
        'https://api.uuni.cn/api/time',
        'http://api.baidu.com/time/get',
        'http://worldtimeapi.org/api/timezone/Asia/Shanghai',
    ]

    def __init__(self):
        self._synced_time: Optional[datetime] = None
        self._last_sync_timestamp: Optional[float] = None
        self._sync_status: str = 'never'
        self._settings_service = None

    @property
    def settings_service(self):
        if self._settings_service is None:
            from app.services.core.settings_service import SettingsService
            self._settings_service = SettingsService
        return self._settings_service

    def is_enabled(self) -> bool:
        setting = self.settings_service.get_setting('enable_time_sync')
        return setting is None or setting is True or setting == 'true'

    def get_sync_interval(self) -> int:
        interval = self.settings_service.get_setting('time_sync_interval')
        if interval and isinstance(interval, int):
            return interval * 60
        return self.DEFAULT_SYNC_INTERVAL

    def get_max_retries(self) -> int:
        retries = self.settings_service.get_setting('time_sync_max_retries')
        if retries and isinstance(retries, int):
            return retries
        return self.DEFAULT_MAX_RETRIES

    def get_server_url(self) -> str:
        url = self.settings_service.get_setting('time_server_url')
        return url or self.DEFAULT_SERVER_URL

    def _fetch_time_from_server(self, url: str) -> Optional[datetime]:
        try:
            with urlopen(url, timeout=3) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    date_str = data.get('date') or data.get('datetime', '').split('+')[0]
                    if date_str:
                        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.warning(f"从 {url} 获取时间失败: {e}")
        return None

    def _try_sync_with_servers(self) -> bool:
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

            if attempt < max_retries - 1:
                logger.info(f"所有服务器同步失败，{self.DEFAULT_RETRY_DELAY}秒后重试...")
                time.sleep(self.DEFAULT_RETRY_DELAY)

        self._sync_status = 'failed'
        logger.error("时间同步失败，已达到最大重试次数")
        return False

    def sync_time(self) -> bool:
        """执行时间同步（由 Cron 服务调用）"""
        if not self.is_enabled():
            logger.info("时间同步已禁用")
            return False
        return self._try_sync_with_servers()

    def get_current_time(self) -> datetime:
        """获取当前时间"""
        if (self._synced_time is not None and
            self._sync_status == 'success' and
            self._last_sync_timestamp is not None):
            elapsed = time.time() - self._last_sync_timestamp
            return self._synced_time + timedelta(seconds=elapsed)
        return datetime.now()

    def get_current_time_str(self, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
        return self.get_current_time().strftime(fmt)

    def get_status(self) -> dict:
        return {
            'status': self._sync_status,
            'synced_time': self._synced_time.strftime('%Y-%m-%d %H:%M:%S') if self._synced_time else None,
            'last_sync_timestamp': self._last_sync_timestamp,
            'enabled': self.is_enabled(),
        }


_time_sync_service: Optional[TimeSyncService] = None


def get_time_sync_service() -> TimeSyncService:
    global _time_sync_service
    if _time_sync_service is None:
        _time_sync_service = TimeSyncService()
    return _time_sync_service
