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

from typing import Any

from django.core.cache import cache

from core.models import SystemSetting


def _convert_setting_value(value: str) -> bool | int | float | str:
    """
    将设置值字符串转换为合适的 Python 类型

    说明：
        数据库中存储的是字符串，此函数根据内容自动转换为：
        - 'true'/'false' -> bool
        - 纯数字（无小数点） -> int
        - 纯数字（有小数点） -> float
        - 其他 -> str

    参数：
        value: 数据库中的字符串值

    返回：
        转换后的 Python 对象
    """
    value = value.strip()
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    elif value.isdigit():
        return int(value)
    elif '.' in value and value.replace('.', '').isdigit():
        return float(value)
    return value


class SettingsService:
    """
    系统设置服务类

    说明：
        负责所有与系统配置相关的操作，是设置数据访问的唯一入口。
        路由层和业务层不应直接操作 SystemSetting 模型。

    类属性：
        DEFAULT_SETTINGS: Dict[str, str] - 默认设置项和值
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

    DEFAULT_SETTINGS = {
        'system_name': '仙芙CIMF',

        'site_logo_enabled': 'true',
        'site_logo_path': '',

        'welcome_title': '欢迎！',
        'welcome_subtitle': '让我们一起把项目完善吧。',
        'welcome_intro': '初始用户名：admin 初始密码：admin123',

        'upload_max_size_mb': '12',
        'upload_max_files': '20',
        'upload_allowed_extensions': 'pdf,doc,docx,xls,xlsx,jpg,png,jpeg,zip,rar',

        'session_timeout_minutes': '30',
        'login_max_failures': '5',
        'login_lock_minutes': '30',

        'enable_audit_log': 'true',
        'log_retention_days': '90',

        'enable_web_watermark': 'false',
        'web_watermark_content': 'username,system_name,datetime',
        'web_watermark_custom_text': '自定义文字',
        'web_watermark_opacity': '0.15',
        'enable_watermark_console_detection': 'false',
        'enable_watermark_shortcut_block': 'false',
        'enable_export_watermark': 'false',

        'enable_time_sync': 'true',
        'time_server_url': 'https://api.uuni.cn/api/time',
        'time_zone': 'Asia/Shanghai',
        'time_sync_interval': '15',
        'time_sync_max_retries': '5',

        'cron_time_sync_enabled': 'true',
        'cron_cache_cleanup_enabled': 'true',
        'cron_email_sending_enabled': 'false',
        'smtp_send_interval': '100',
        'cron_email_cleanup_enabled': 'false',
        'cron_email_cleanup_interval': '86400',

        'maintenance_mode': 'false',
        'allow_registration': 'false',

        'smtp_enabled': 'false',
        'smtp_provider': 'gmail_tls',
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': '587',
        'smtp_use_ssl': 'false',
        'smtp_use_tls': 'true',
        'smtp_username': '',
        'smtp_from_email': '',
        'smtp_from_name': '仙芙CIMF',
        'smtp_timeout': '30',
        'smtp_skip_verify': 'false',
        'smtp_password': '',
        'smtp_retry_count': '3',
        'smtp_batch_size': '10',
        'smtp_rate_limit': '0',
        'smtp_log_days': '30',
        'smtp_failed_notify': 'false',
        'smtp_notify_email': '',
        'smtp_system_url': '',
    }

    BOOL_SETTINGS = {
        'enable_audit_log', 'enable_web_watermark', 'enable_watermark_console_detection',
        'enable_watermark_shortcut_block', 'enable_export_watermark',
        'cron_time_sync_enabled', 'cron_cache_cleanup_enabled', 'site_logo_enabled',
    }

    CACHE_KEY = 'system_settings_all'
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
        result = dict(cls.DEFAULT_SETTINGS)

        for setting in settings:
            result[setting.key] = _convert_setting_value(setting.value)

        cache.set(cls.CACHE_KEY, result, cls.CACHE_TTL)
        return result if as_dict else settings

    @classmethod
    def get_setting(cls, key: str, default: Any = None) -> Any:
        """
        获取单个系统设置

        说明：
            从数据库或缓存读取单个设置值。
            如果数据库中不存在，返回默认值。

        参数：
            key: 设置项的 key
            default: 不存在时的默认值

        返回：
            设置值（自动转换类型）
        """
        all_settings = cls.get_all_settings()
        return all_settings.get(key, cls.DEFAULT_SETTINGS.get(key, default))

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
            key=key,
            defaults={
                'value': value_str,
                'description': description or f'系统设置 - {key}'
            }
        )

        cls.clear_cache()
        return setting

    @classmethod
    def save_settings_bulk(cls, settings_dict: dict[str, Any]) -> int:
        """
        批量保存系统设置

        说明：
            批量保存多个设置项，最后统一清除缓存。

        参数：
            settings_dict: 设置字典

        返回：
            保存的设置项数量
        """
        updated_count = 0
        for key, value in settings_dict.items():
            if key in cls.DEFAULT_SETTINGS or SystemSetting.objects.filter(key=key).exists():
                if key == 'web_watermark_content' and isinstance(value, list):
                    value_str = ','.join(value)
                else:
                    value_str = str(value).strip()

                SystemSetting.objects.update_or_create(
                    key=key,
                    defaults={
                        'value': value_str,
                        'description': f'系统设置 - {key}'
                    }
                )
                updated_count += 1

        if updated_count:
            cls.clear_cache()

        return updated_count

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
            if key in cls.DEFAULT_SETTINGS:
                cls.save_setting(key, cls.DEFAULT_SETTINGS[key])
                return 1
            return 0

        return cls._reset_to_default_bulk()

    @classmethod
    def _reset_to_default_bulk(cls) -> int:
        """批量重置所有设置到默认值"""
        updated = 0
        for key, default_value in cls.DEFAULT_SETTINGS.items():
            _, _created = SystemSetting.objects.update_or_create(
                key=key,
                defaults={
                    'value': str(default_value).strip(),
                    'description': f'系统设置 - {key}'
                }
            )
            updated += 1

        cls.clear_cache()
        return updated

    @classmethod
    def clear_cache(cls):
        """
        清除缓存
        """
        cache.delete(cls.CACHE_KEY)
