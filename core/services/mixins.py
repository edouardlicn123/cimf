import logging
import threading
import time

from django.core.cache import cache

logger = logging.getLogger(__name__)


class SingletonMixin:
    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):  # noqa: ARG004
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance


class CachedServiceMixin:
    cache_key_prefix = ""
    cache_ttl = 60

    @classmethod
    def _get_cached(cls, fetch_fn, key_suffix=""):
        full_key = f"{cls.cache_key_prefix}{key_suffix}"
        cached = cache.get(full_key)
        if cached is not None:
            return cached
        data = fetch_fn()
        cache.set(full_key, data, cls.cache_ttl)
        return data

    @classmethod
    def _invalidate_cache(cls, key_suffix=""):
        full_key = f"{cls.cache_key_prefix}{key_suffix}"
        cache.delete(full_key)


def success_response(**kwargs):
    return {"success": True, **kwargs}


def error_response(message, **kwargs):
    return {"success": False, "error": message, **kwargs}


def clean_str(value, default=""):
    if value is None:
        return default
    return str(value).strip()


def clean_optional_str(value):
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned if cleaned else None


def safe_execute(fn, error_return=None, log_msg="操作失败", logger=None):
    try:
        return fn()
    except Exception as e:
        if logger:
            logger.error(f"{log_msg}: {e}", exc_info=True)
        return error_return


_sentinel = object()


def update_fields(instance, **fields):
    changed_fields = []
    for key, value in fields.items():
        if getattr(instance, key) != value:
            setattr(instance, key, value)
            changed_fields.append(key)
    if changed_fields:
        instance.save(update_fields=changed_fields)
    return instance


def retry_with_fallbacks(sources, fetch_fn, max_retries=1, retry_delay=2, timeout=30):
    last_error = None
    for attempt in range(max_retries):
        for source in sources:
            try:
                return fetch_fn(source, timeout)
            except Exception as e:
                last_error = e
                logger.warning(f"获取源 {source} 失败: {e}", exc_info=True)
                continue
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
    raise last_error
