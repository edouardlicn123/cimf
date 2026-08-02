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
from datetime import UTC, datetime, timedelta
from urllib.request import urlopen
from zoneinfo import ZoneInfo

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
        "http://worldtimeapi.org/api/timezone/Asia/Shanghai",
        "http://quan.suning.com/getSysTime.do",
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
        except Exception as e:
            logger.warning("获取设置值失败: key=%s, error=%s", key, e)
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

    def test_connection(self, url: str | None = None) -> datetime | None:
        """测试时间服务器连接（公开入口）"""
        return self._fetch_time_from_server(url or self.get_server_url())

    def _fetch_time_from_server(self, url: str) -> datetime | None:
        """从指定服务器获取时间"""

        def _fetch():
            with urlopen(url, timeout=5) as response:  # noqa: S310 — trusted time API server
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    # 优先使用服务器权威 epoch 字段（时区无关，避免墙钟被误当 UTC）
                    ts = data.get("timestamp") or data.get("unixtime")
                    if ts:
                        return datetime.fromtimestamp(int(ts), tz=UTC)
                    date_str = (
                        data.get("datetime")
                        or data.get("date")
                        or data.get("dateTime")
                        or data.get("sysTime2")
                    )
                    if date_str:
                        date_str = str(date_str)
                        # 先尝试带时区偏移的 ISO 格式（如 worldtimeapi 的 +08:00）
                        try:
                            parsed = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                            if parsed.tzinfo is not None:
                                return parsed
                        except ValueError:
                            pass
                        # 无偏移的裸墙钟（uuni/suning 返回北京时间）按配置时区解释，勿默认 UTC
                        tz_name = self._get_settings_value("time_zone") or "Asia/Shanghai"
                        return datetime.strptime(date_str[:19], "%Y-%m-%d %H:%M:%S").replace(
                            tzinfo=ZoneInfo(tz_name)
                        )
            return None

        return safe_execute(_fetch, error_return=None, log_msg=f"从 {url} 获取时间失败", logger=logger)

    def _try_sync_with_servers(self) -> bool:
        """尝试从服务器同步时间"""
        servers = [self.get_server_url(), *self.BACKUP_SERVERS]
        servers = list(dict.fromkeys(servers))
        max_retries = self.get_max_retries()
        failed_servers: set[str] = set()

        for attempt in range(max_retries):
            available = [s for s in servers if s not in failed_servers]
            if not available:
                break

            for server_url in available:
                logger.info(f"尝试从 {server_url} 同步时间 (尝试 {attempt + 1}/{max_retries})")
                server_time = self._fetch_time_from_server(server_url)
                if server_time:
                    self._synced_time = server_time
                    self._last_sync_timestamp = time.time()
                    self._sync_status = "success"
                    logger.info(f"时间同步成功: {server_time}")
                    return True
                failed_servers.add(server_url)

            if attempt < max_retries - 1:
                retry_servers = [s for s in servers if s not in failed_servers]
                if retry_servers:
                    logger.info(f"部分服务器失败，{self.DEFAULT_RETRY_DELAY}秒后重试可用服务器...")
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
        """获取当前时间（返回配置时区本地化 datetime，strftime 即显示墙钟）"""

        def _to_local(dt: datetime) -> datetime:
            tz_name = self._get_settings_value("time_zone") or "Asia/Shanghai"
            return dt.astimezone(ZoneInfo(tz_name))

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
                    return _to_local(synced + timedelta(seconds=elapsed))
        except Exception as e:
            logger.warning(f"从 DB 读取同步时间失败: {e}")

        # ── 第二优先：内存缓存（进程内第二次调用时更快） ──
        if self._synced_time is not None and self._sync_status == "success" and self._last_sync_timestamp is not None:
            elapsed = time.time() - self._last_sync_timestamp
            return _to_local(self._synced_time + timedelta(seconds=elapsed))

        # ── 第三优先：兜底 ──
        return _to_local(now())

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
