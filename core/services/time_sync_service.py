"""
================================================================================
文件：time_sync_service.py
路径：/home/edo/cimf-v2/core/services/time_sync_service.py
================================================================================

    功能说明：
    时钟同步服务，负责与远程时间服务器同步系统时间。

    主要功能：
    - 并行采集多个独立时间服务器
    - 多数收敛：多个时间源中找彼此接近的众数，抗单源失效/漂移
    - 服务器健康动态排序：持续失败的服务器自动降级、移出采集池
    - 统一换算 UTC：各源通过 utcOffset/timeZone 归一
    - 失败时返回本地时间作为备选

    设计说明：
    - 此服务不直接管理调度，由 CronService 的 TimeSyncTask 调用
    - 并行化保证：即使个别服务器超时，整体耗时约等于最慢服务器，而非逐个累加

版本：
    - 1.0: 从 Flask 迁移

依赖：
    - urllib.request: 网络请求
    - json: JSON 解析
"""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime, timedelta
from urllib.request import urlopen
from zoneinfo import ZoneInfo

from django.utils.timezone import now

from core.services.mixins import SingletonMixin, safe_execute

logger = logging.getLogger(__name__)

# 相邻服务器返回时间允许的最大偏差（秒），超过则视为漂移/异常源
_MAX_TIME_DIFF = 5

# 单个服务器在一次同步周期内的最大超时（秒），并行请求下限制整体耗时
_REQUEST_TIMEOUT = 5

# 服务器历史健康记录 {url: 连续失败次数}；连续失败超过该阈值则临时降级到队列末尾
_MAX_CONSECUTIVE_FAILURES = 3


def _parse_iso_naive(s: str) -> datetime | None:
    """解析不含时区信息的 ISO 时间字符串（如 '2026-08-29T13:41:46.6641224' 或 '2026-08-29T05:41Z'）"""
    try:
        s = s.strip().rstrip("Z")
        parsed = datetime.fromisoformat(s)
        return parsed
    except ValueError:
        try:
            return datetime.strptime(s[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S")  # noqa: DTZ007 — 返回 naive，由调用方 attach tz
        except ValueError:
            return None


def _attach_timezone(naive: datetime, hint: str, default_tz: str) -> datetime | None:
    """将 naive datetime 应用到 hint 指定的时区偏移/名称上，返回 aware datetime（保留原墙钟）或 None"""
    hint = hint.strip()
    try:
        # 形如 '+08:00' / '-05:00' / '00:00:00' 的偏移 → 固定偏移时区
        if hint.startswith(("+", "-")) or (":" in hint and not hint[:3].isalpha()):
            offset = _parse_utc_offset(hint)
            if offset is not None:
                # +08:00 表示墙钟 = UTC+8 → 附上该固定偏移
                return _apply_fixed_offset(naive, offset)
        # 形如 'Asia/Shanghai' / 'UTC' 的时区名
        return naive.replace(tzinfo=ZoneInfo(hint))
    except (ValueError, KeyError, NameError):
        try:
            return naive.replace(tzinfo=ZoneInfo(default_tz))
        except (ValueError, KeyError, NameError, ModuleNotFoundError):
            return None


def _apply_fixed_offset(naive: datetime, offset: timedelta) -> datetime:
    """墙钟直接附上固定偏移（+08:00 即墙钟=UTC+8），返回 aware datetime"""
    from datetime import timezone as dt_timezone  # noqa: PLC0415

    return naive.replace(tzinfo=dt_timezone(offset))


def _parse_utc_offset(value: str) -> timedelta | None:
    """解析 utcOffset（如 '+08:00' / '-05:00' / '00:00:00'）为 timedelta"""
    try:
        s = str(value).strip()
        sign = -1 if s.startswith("-") else 1
        digits = s.lstrip("+-").split(":")
        hours = int(digits[0])
        minutes = int(digits[1]) if len(digits) > 1 else 0
        seconds = int(digits[2]) if len(digits) > 2 else 0
        return sign * timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except (ValueError, IndexError, TypeError):
        return None


class TimeSyncService(SingletonMixin):
    """
    时钟同步服务类
    """

    DEFAULT_SYNC_INTERVAL = 15 * 60  # 15分钟
    DEFAULT_MAX_RETRIES = 5
    DEFAULT_RETRY_DELAY = 2
    DEFAULT_SERVER_URL = "https://timeapi.io/api/time/current/zone?timeZone=Asia/Shanghai"
    MAX_SYNC_AGE = 24 * 3600  # 同步基准超过该时长视为过期，降级到本地时间，避免显示陈旧/脏值

    # 多源时间服务器池：并行采集 + 多数收敛，避免单点失效/漂移
    TIME_SERVERS = [
        "https://timeapi.io/api/time/current/zone?timeZone=Asia/Shanghai",
        "https://timeapi.io/api/time/current/zone?timeZone=UTC",
        "http://worldclockapi.com/api/json/utc/now",
        "https://time.now/developer/api/timezone/Asia/Shanghai",
        "https://time.now/developer/api/timezone/UTC",
    ]

    # 模块级服务器健康记录 {url: 连续失败次数}
    _server_failures: dict[str, int] = {}

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

    def _fetch_time_from_server(self, url: str, silent: bool = False) -> datetime | None:
        """从指定服务器获取时间（统一换算为 UTC）

        兼容的时间源字段：
        - epoch: timestamp / unixtime
        - 带时区 ISO: datetime / dateTime（如 worldtimeapi 的 +08:00、timeapi.io 的 Z）
        - 裸墙钟 + 偏移字段: dateTime / currentDateTime + utcOffset 或 timeZone

        silent=True 时静默捕获异常返回 None（供并行采集使用，单源失败属常态，
        不刷日志，由健康机制降级 + 整体失败时才记录）。
        """

        def _fetch():
            with urlopen(url, timeout=_REQUEST_TIMEOUT) as response:  # noqa: S310 — trusted time API server
                if response.status != 200:
                    return None
                data = json.loads(response.read().decode("utf-8"))
                # 优先使用服务器权威 epoch 字段（时区无关，避免墙钟被误当 UTC）
                ts = data.get("timestamp") or data.get("unixtime")
                if ts:
                    return datetime.fromtimestamp(int(ts), tz=UTC)
                date_str = (
                    data.get("datetime")
                    or data.get("dateTime")
                    or data.get("currentDateTime")
                    or data.get("sysTime2")
                    or data.get("date")
                )
                if not date_str or not str(date_str):
                    return None
                s = str(date_str)

                # ── 情况 A：带时区 offset 或 tz 字段的裸墙钟（worldclockapi / timeapi.io 等）──
                tz_hint = data.get("utcOffset") or data.get("timeZone") or data.get("utc_offset")
                if tz_hint:
                    naive = _parse_iso_naive(s)
                    if naive is not None:
                        aware = _attach_timezone(naive, str(tz_hint), self._get_settings_value("time_zone") or "Asia/Shanghai")
                        if aware is not None:
                            return aware.astimezone(UTC)

                # ── 情况 B：带时区偏移的 ISO 格式（如 worldtimeapi 的 +08:00 / timeapi.io 的 Z）──
                try:
                    parsed = datetime.fromisoformat(s.replace("Z", "+00:00"))
                    if parsed.tzinfo is not None:
                        return parsed.astimezone(UTC)
                except ValueError:
                    pass

                # ── 情况 C：无偏移裸墙钟，按配置时区解释 ──
                tz_name = self._get_settings_value("time_zone") or "Asia/Shanghai"
                for fmt in ("%Y-%m-%d %H:%M:%S", "%m/%d/%Y"):
                    try:
                        return datetime.strptime(s[:19], fmt).replace(
                            tzinfo=ZoneInfo(tz_name)
                        ).astimezone(UTC)
                    except ValueError:
                        continue
            return None

        if silent:
            try:
                return _fetch()
            except Exception:
                return None
        msg = f"从 {url} 获取时间失败"
        return safe_execute(_fetch, error_return=None, log_msg=msg, logger=logger, log_fn=logger.warning)

    def _collect_server_times(self, servers: list[str]) -> list[tuple[str, datetime | None]]:
        """多线程并行采集多个服务器时间，返回 (url, 成功时间 or None) 列表"""
        results: list[tuple[str, datetime | None]] = []
        with ThreadPoolExecutor(max_workers=len(servers)) as executor:
            future_map = {executor.submit(self._fetch_time_from_server, s, silent=True): s for s in servers}
            for future in as_completed(future_map):
                url = future_map[future]
                try:
                    result = future.result()
                except Exception as e:  # pragma: no cover
                    logger.warning("时间服务器采集异常: %s: %s", url, e)
                    result = None
                results.append((url, result))
        return results

    def _converge(self, times: list[datetime]) -> datetime | None:
        """多数收敛：在多个时间源中找出彼此接近的众数，容忍一个异常/漂移源

        - 1 个成功：直接采用（记 warning）
        - ≥2 个成功：以某源为基准，统计与其差值 < _MAX_TIME_DIFF 的同伴数；
          若大多数源一致（允许 1 个异常值），取该簇；否则拒绝（分歧过大）
        """
        if not times:
            return None
        if len(times) == 1:
            logger.warning("时间源只有 %d 个成功，无法交叉校验", len(times))
            return times[0]

        # 找出同伴最多的基准
        best = max(times, key=lambda t: sum(1 for u in times if abs((t - u).total_seconds()) < _MAX_TIME_DIFF))
        peers = [u for u in times if abs((best - u).total_seconds()) < _MAX_TIME_DIFF]
        if len(peers) >= max(1, len(times) - 1):
            return best
        logger.warning(
            "时间源分歧过大: 成功 %d 个，一致 %d 个，拒绝采用", len(times), len(peers)
        )
        return None

    def _ordered_servers(self) -> list[str]:
        """按健康度排序服务器：连续失败次数少的排前（死的排后），避免每次都等挂掉服务器。

        连续失败超过 _MAX_CONSECUTIVE_FAILURES 的服务器暂时移出采集池，
        但保留至少 2 个服务器（含健康探针），避免池子为空。
        """
        custom = self.get_server_url()
        server_list = list(dict.fromkeys([custom, *self.TIME_SERVERS]))
        # 排序：失败次数少的在前
        server_list.sort(key=lambda s: self._server_failures.get(s, 0))
        # 过滤持续失败的服务器，但保留前 2 个（含配置值）以便偶发探活
        active = [s for s in server_list if self._server_failures.get(s, 0) < _MAX_CONSECUTIVE_FAILURES]
        if len(active) < 2:
            return server_list[:2]
        return active

    def _update_health(self, results: list[tuple[str, datetime | None]]) -> None:
        """更新服务器健康记录"""
        for url, t in results:
            if t is not None:
                self._server_failures[url] = 0
            else:
                self._server_failures[url] = self._server_failures.get(url, 0) + 1

    def _try_sync_with_servers(self) -> bool:
        """并行采集多个时间源并多数收敛出一个可信时间"""
        servers = self._ordered_servers()
        max_retries = self.get_max_retries()
        failed_servers: set[str] = set()

        for attempt in range(max_retries):
            available = [s for s in servers if s not in failed_servers]
            if not available:
                break

            logger.info("并行采集 %d 个时间源 (尝试 %d/%d)", len(available), attempt + 1, max_retries)
            results = self._collect_server_times(available)
            success_times = [t for _, t in results if t is not None]
            self._update_health(results)

            converged = self._converge(success_times)
            if converged:
                self._synced_time = converged
                self._last_sync_timestamp = time.time()
                self._sync_status = "success"
                logger.info(
                    "时间同步成功（%d/%d 个源一致）: %s",
                    len([t for t in success_times if abs((converged - t).total_seconds()) < _MAX_TIME_DIFF]),
                    len(success_times),
                    converged,
                )
                return True

            for url, t in results:
                if t is None:
                    failed_servers.add(url)

            if attempt < max_retries - 1:
                logger.info("%d秒后重试可用时间源...", self.DEFAULT_RETRY_DELAY)
                time.sleep(self.DEFAULT_RETRY_DELAY)

        self._sync_status = "failed"
        logger.error("时间同步失败，已达到最大重试次数，不可达源: %s", sorted(failed_servers) or "（全部）")
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
                logger.info("持久化同步时间成功: %s", self._synced_time.isoformat())
            except Exception as e:
                logger.error("持久化同步时间失败: %s", e)
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
                if 0 <= elapsed <= self.MAX_SYNC_AGE:
                    return _to_local(synced + timedelta(seconds=elapsed))
                if elapsed > self.MAX_SYNC_AGE:
                    logger.warning(
                        "持久化同步时间已过期(%.0fs > %ds)，降级到本地时间",
                        elapsed,
                        self.MAX_SYNC_AGE,
                    )
        except Exception as e:
            logger.warning("从 DB 读取同步时间失败: %s", e)

        # ── 第二优先：内存缓存（进程内第二次调用时更快） ──
        if self._synced_time is not None and self._sync_status == "success" and self._last_sync_timestamp is not None:
            elapsed = time.time() - self._last_sync_timestamp
            if 0 <= elapsed <= self.MAX_SYNC_AGE:
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
