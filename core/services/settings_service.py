"""
================================================================================
文件：settings_service.py
路径：/home/edo/cimf-v2/core/services/settings_service.py
================================================================================

功能说明：
    系统全局设置服务，管理和提供系统配置参数。

    主要功能：
    - 读取/保存系统设置项
    - 设置值类型自动转换（字符串转布尔/整数/浮点数）
    - 设置缓存机制，提高读取性能
    - 批量保存设置
    - 重置设置为默认值

    设计原则：
    - 单一数据源：所有设置存储在 SystemSetting 数据库表中
    - 缓存优化：读取设置时使用内存缓存，减少数据库查询
    - 类型安全：自动将数据库字符串值转换为合适的 Python 类型

用法：
    1. 读取单个设置：
        value = SettingsService.get_setting('system_name')

    2. 读取所有设置：
        settings = SettingsService.get_all_settings()

    3. 保存设置：
        SettingsService.save_setting('system_name', '新名称')

    4. 批量保存：
        SettingsService.save_settings_bulk({'key1': 'value1', 'key2': 'value2'})

版本：
    - 1.0: 从 Flask 迁移

依赖：
    - core.models.SystemSetting: 系统设置数据模型
"""

import json
import logging
from typing import Any

from django.core.cache import cache

from core.models import SystemSetting
from core.services.mixins import CachedServiceMixin
from core.settings_meta import SETTINGS_META

logger = logging.getLogger(__name__)


def _convert_setting_value(value: str) -> bool | int | float | str:
    value = value.strip()
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    try:
        return int(value)
    except (ValueError, TypeError):
        pass
    try:
        return float(value)
    except (ValueError, TypeError):
        pass
    return value


class SettingsService(CachedServiceMixin):
    """
    系统设置服务类

    说明：
        负责所有与系统配置相关的操作，是设置数据访问的唯一入口。
        路由层和业务层不应直接操作 SystemSetting 模型。

    类属性：
        SETTINGS_META: dict - 设置项元数据（default + type）
        CACHE_KEY: str - 缓存键名
        CACHE_TTL: int - 缓存过期时间（秒）

    方法：
        get_all_settings(): 获取所有设置
        get_setting(): 获取单个设置
        save_setting(): 保存单个设置
        save_settings_bulk(): 批量保存设置
        reset_to_default(): 重置为默认值
        clear_cache(): 清除缓存
    """

    SETTINGS_META = SETTINGS_META

    @classmethod
    def _get_default_settings(cls) -> dict[str, str]:
        return {k: v["default"] for k, v in cls.SETTINGS_META.items()}

    CACHE_KEY = "system_settings_all"
    CACHE_TTL = 60

    @classmethod
    def get_all_settings(cls, as_dict: bool = True) -> dict[str, Any]:
        """
        获取所有系统设置

        说明：
            从数据库读取所有设置，与默认值合并后返回。
            结果会被缓存以提高性能。

        参数：
            as_dict: 是否返回字典格式，False 返回数据库模型列表

        返回：
            设置字典或数据库模型列表
        """
        cached = cache.get(cls.CACHE_KEY)
        if cached is not None:
            return cached if as_dict else SystemSetting.objects.all()

        settings = SystemSetting.objects.all()
        result = cls._get_default_settings()

        for setting in settings:
            result[setting.key] = _convert_setting_value(setting.value)

        cache.set(cls.CACHE_KEY, result, cls.CACHE_TTL)
        return result if as_dict else settings

    @classmethod
    def get_setting(cls, key: str, default: Any = None, parse_json: bool = False) -> Any:
        """
        获取单个系统设置

        说明：
            从数据库或缓存读取单个设置值。
            如果数据库中不存在，返回默认值。

        参数：
            key: 设置项的 key
            default: 不存在时的默认值
            parse_json: 是否将值解析为 JSON

        返回：
            设置值（自动转换类型）
        """
        if parse_json:
            setting = SystemSetting.objects.filter(key=key).first()
            if not setting:
                return default
            try:
                return json.loads(setting.value)
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning("设置项 %s 不是有效的 JSON: %s — %s", key, setting.value, e)
                return default
        all_settings = cls.get_all_settings()
        return all_settings.get(key, cls._get_default_settings().get(key, default))

    @classmethod
    def save_setting(cls, key: str, value: Any, description: str | None = None) -> SystemSetting:
        """
        保存单个系统设置

        说明：
            保存设置到数据库，并清除缓存。

        参数：
            key: 设置项的 key
            value: 设置值（会自动转换为字符串）
            description: 设置描述（可选）

        返回：
            SystemSetting 模型实例
        """
        value_str = str(value).strip()

        setting, _created = SystemSetting.objects.update_or_create(
            key=key, defaults={"value": value_str, "description": description or f"系统设置 - {key}"}
        )

        cls.clear_cache()
        return setting

    @classmethod
    def save_settings_bulk(cls, settings_dict: dict[str, Any]) -> None:
        """
        批量保存系统设置

        说明：
            批量保存多个设置项，逐项写入后统一清除缓存。

        参数：
            settings_dict: 设置字典
        """
        for key, raw_val in settings_dict.items():
            actual_val = ",".join(raw_val) if key == "web_watermark_content" and isinstance(raw_val, list) else raw_val
            value_str = str(actual_val).strip()
            SystemSetting.objects.update_or_create(
                key=key, defaults={"value": value_str, "description": f"系统设置 - {key}"}
            )
        cls.clear_cache()

    @classmethod
    def reset_to_default(cls, key: str | None = None) -> int:
        """
        重置设置为默认值（优化版）

        说明：
            将指定设置项或所有设置项重置为默认值。
            批量写入后统一清除缓存，避免频繁清除。

        参数：
            key: 要重置的设置 key，None 表示重置所有

        返回：
            重置的设置项数量
        """
        if key:
            defaults = cls._get_default_settings()
            if key in defaults:
                cls.save_setting(key, defaults[key])
                return 1
            return 0

        return cls._reset_to_default_bulk()

    @classmethod
    def _reset_to_default_bulk(cls) -> int:
        """批量重置所有设置到默认值"""
        updated = 0
        for key, default_value in cls._get_default_settings().items():
            _, _created = SystemSetting.objects.update_or_create(
                key=key, defaults={"value": str(default_value).strip(), "description": f"系统设置 - {key}"}
            )
            updated += 1

        cls.clear_cache()
        return updated

    @classmethod
    def get_count(cls) -> int:
        """获取系统设置总数"""
        from core.models import SystemSetting  # noqa: PLC0415

        return SystemSetting.objects.count()

    @classmethod
    def clear_cache(cls):
        """
        清除缓存
        """
        cache.delete(cls.CACHE_KEY)
