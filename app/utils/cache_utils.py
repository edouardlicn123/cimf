# 文件路径：app/utils/cache_utils.py
# 功能说明：通用缓存工具类，提供内存缓存功能

import time
from typing import Any, Callable, Optional


class CacheManager:
    """通用缓存管理器"""
    
    def __init__(self, default_ttl: int = 60):
        """
        Args:
            default_ttl: 默认缓存过期时间（秒）
        """
        self._cache = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值，如果过期或不存在返回 None"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if time.time() - entry['timestamp'] > entry['ttl']:
            del self._cache[key]
            return None
        
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存值"""
        self._cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl if ttl is not None else self.default_ttl
        }
    
    def delete(self, key: str):
        """删除指定缓存"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        """清空所有缓存"""
        self._cache.clear()
    
    def get_or_set(self, key: str, factory: Callable[[], Any], ttl: Optional[int] = None) -> Any:
        """获取缓存值，如果不存在则调用 factory 生成并缓存"""
        value = self.get(key)
        if value is None:
            value = factory()
            self.set(key, value, ttl)
        return value


# 全局缓存实例
_system_cache = CacheManager(default_ttl=60)


def get_system_cache() -> CacheManager:
    """获取系统级缓存实例"""
    return _system_cache


def cache_get(key: str) -> Optional[Any]:
    """快捷方法：获取缓存"""
    return _system_cache.get(key)


def cache_set(key: str, value: Any, ttl: Optional[int] = None):
    """快捷方法：设置缓存"""
    _system_cache.set(key, value, ttl)


def cache_delete(key: str):
    """快捷方法：删除缓存"""
    _system_cache.delete(key)


def cache_clear():
    """快捷方法：清空缓存"""
    _system_cache.clear()
