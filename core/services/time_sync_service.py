"""
================================================================================
文件：time_sync_service.py
路径：/home/edo/cimf-v2/core/services/time_sync_service.py
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

版本：
    - 1.0: 从 Flask 迁移

依赖：
    - urllib.request: 网络请求
    - json: JSON 解析
"""

import json
import logging
import time
from datetime import datetime, timedelta
from urllib.request import urlopen

from django.utils.timezone import now

from core.services.mixins import SingletonMixin, safe_execute

logger = logging.getLogger(__name__)


class TimeSyncService(SingletonMixin):
    """
    时钟同步服务类
    """

    DEFAULT_SYNC_INTERVAL = 15 * 60  # 15分钟
    DEFAULT_MAX_RETRIES = 5
    DEFAULT_RETRY_DELAY = 2
    DEFAULT_SERVER_URL = "https://api.uuni.cn/api/time"

    BACKUP_SERVERS = [
        "https://api.uuni.cn/api/time",
        "http://api.baidu.com/time/get",
        "http://worldtimeapi.org/api/timezone/Asia/Shanghai",
    ]

    def __init__(self):
        self._synced_time: datetime | None = None
        self._last_sync_timestamp: float | None = None
        self._sync_status: str = "never"

    @staticmethod
    def _get_settings_value(key, default=None):
        try:
            from core.services import SettingsService  # noqa: PLC0415

            value = SettingsService.get_setting(key)
            return value if value is not None else default
        except Exception:
            return default

    def is_enabled(self) -> bool:
        """检查时间同步是否启用"""
        setting = self._get_settings_value("enable_time_sync", True)
        return setting is None or setting is True or str(setting).lower() == "true"

    def get_sync_interval(self) -> int:
        """获取同步间隔（秒）"""
        interval = self._get_settings_value("time_sync_interval")
        if interval and isinstance(interval, int):
            return interval * 60
        return self.DEFAULT_SYNC_INTERVAL

    def get_max_retries(self) -> int:
        """获取最大重试次数"""
        retries = self._get_settings_value("time_sync_max_retries")
        if retries and isinstance(retries, int):
            return retries
        return self.DEFAULT_MAX_RETRIES

    def get_server_url(self) -> str:
        """获取时间服务器 URL"""
        url = self._get_settings_value("time_server_url")
        return url or self.DEFAULT_SERVER_URL

    def _fetch_time_from_server(self, url: str) -> datetime | None:
        """从指定服务器获取时间"""

        def _fetch():
            with urlopen(url, timeout=3) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    date_str = data.get("date") or data.get("datetime", "").split("+")[0].replace("T", " ")
                    if date_str:
                        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=None)
            return None

        return safe_execute(_fetch, error_return=None, log_msg=f"从 {url} 获取时间失败", logger=logger)

    def _try_sync_with_servers(self) -> bool:
        """尝试从服务器同步时间"""
        servers = [self.get_server_url(), *self.BACKUP_SERVERS]
        servers = list(dict.fromkeys(servers))
        max_retries = self.get_max_retries()

        for attempt in range(max_retries):
            for server_url in servers:
                logger.info(f"尝试从 {server_url} 同步时间 (尝试 {attempt + 1}/{max_retries})")
                server_time = self._fetch_time_from_server(server_url)
                if server_time:
                    self._synced_time = server_time
                    self._last_sync_timestamp = time.time()
                    self._sync_status = "success"
                    logger.info(f"时间同步成功: {server_time}")
                    return True

            if attempt < max_retries - 1:
                logger.info(f"所有服务器同步失败，{self.DEFAULT_RETRY_DELAY}秒后重试...")
                time.sleep(self.DEFAULT_RETRY_DELAY)

        self._sync_status = "failed"
        logger.error("时间同步失败，已达到最大重试次数")
        return False

    def sync_time(self) -> bool:
        """执行时间同步"""
        if not self.is_enabled():
            logger.info("时间同步已禁用")
            return False

        result = self._try_sync_with_servers()
        if result and self._synced_time is not None:
            try:
                from core.services import SettingsService  # noqa: PLC0415

                SettingsService.save_setting("system_synced_time", self._synced_time.isoformat())
                SettingsService.save_setting("system_sync_monotonic", str(time.monotonic()))
                logger.info(f"持久化同步时间成功: {self._synced_time.isoformat()}")
            except Exception as e:
                logger.error(f"持久化同步时间失败: {e}")
        return result

    def get_current_time(self) -> datetime:
        """获取当前时间"""
        # ── 第一优先：从 DB 读取持久化的同步基准 ──
        try:
            from core.services import SettingsService  # noqa: PLC0415

            synced_str = SettingsService.get_setting("system_synced_time")
            monotonic_str = SettingsService.get_setting("system_sync_monotonic")

            if synced_str and monotonic_str:
                synced = datetime.fromisoformat(synced_str)
                if synced.tzinfo is None:
                    from django.utils.timezone import make_aware  # noqa: PLC0415
                    synced = make_aware(synced)
                mono = float(monotonic_str)
                elapsed = time.monotonic() - mono
                if elapsed >= 0:
                    return synced + timedelta(seconds=elapsed)
        except Exception as e:
            logger.warning(f"从 DB 读取同步时间失败: {e}")

        # ── 第二优先：内存缓存（进程内第二次调用时更快） ──
        if self._synced_time is not None and self._sync_status == "success" and self._last_sync_timestamp is not None:
            elapsed = time.time() - self._last_sync_timestamp
            return self._synced_time + timedelta(seconds=elapsed)

        # ── 第三优先：兜底 ──
        return now()

    def get_current_time_str(self, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """获取当前时间字符串"""
        return self.get_current_time().strftime(fmt)

    def get_status(self) -> dict:
        """获取同步状态"""
        from core.services import SettingsService  # noqa: PLC0415

        synced_str = SettingsService.get_setting("system_synced_time")
        return {
            "status": self._sync_status,
            "synced_time": self._synced_time.isoformat() if self._synced_time else None,
            "persisted_synced_time": synced_str,
            "last_sync_timestamp": self._last_sync_timestamp,
            "enabled": self.is_enabled(),
        }


def get_time_sync_service() -> TimeSyncService:
    """获取时间同步服务单例"""
    return TimeSyncService()
