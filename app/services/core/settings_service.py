# 文件路径：app/services/settings_service.py
# 更新日期：2026-03-15
# 功能说明：系统全局设置的核心业务逻辑，包括读取所有设置，保存/更新设置项、类型转换校验、默认值处理等

import time
from typing import Dict, Any, Optional, Union
from flask import current_app
from app import db
from app.models import SystemSetting
from datetime import datetime


def _convert_setting_value(value: str) -> Union[bool, int, float, str]:
    """将设置值字符串转换为合适的类型"""
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
    系统设置服务层
    负责所有与系统配置相关的操作，路由层不应直接操作 SystemSetting 模型或 db.session
    """

    DEFAULT_SETTINGS = {
        # 系统基本信息
        'system_name': 'CIMF',

        # 上传相关
        'upload_max_size_mb': '12',
        'upload_max_files': '20',
        'upload_allowed_extensions': 'pdf,doc,docx,xls,xlsx,jpg,png,jpeg,zip,rar',

        # 会话与安全
        'session_timeout_minutes': '30',
        'login_max_failures': '5',
        'login_lock_minutes': '30',

        # 日志与审计
        'enable_audit_log': 'true',
        'log_retention_days': '90',

        # 网页水印设置
        'enable_web_watermark': 'false',
        'web_watermark_content': 'username,system_name,datetime',
        'web_watermark_custom_text': '自定义文字<system',
        'web_watermark_opacity': '0.15',
        'enable_watermark_console_detection': 'false',
        'enable_watermark_shortcut_block': 'false',
        'enable_export_watermark': 'false',

        # 时间管理
        'enable_time_sync': 'true',
        'time_server_url': 'https://api.uuni.cn/api/time',
        'time_zone': 'Asia/Shanghai',
        'time_sync_interval': '15',
        'time_sync_max_retries': '5',

        # Cron 调度任务设置
        'cron_time_sync_enabled': 'true',
        'cron_cache_cleanup_enabled': 'true',
        'cron_cache_cleanup_interval': '10800',  # 3小时

        # 其他全局开关
        'maintenance_mode': 'false',
        'allow_registration': 'false',
    }

    _cache = {
        'all_settings': {'data': None, 'timestamp': 0},
        'single_setting': {},
    }
    CACHE_TTL = 60

    @classmethod
    def _get_cached_all_settings(cls) -> Optional[Dict[str, Any]]:
        now = time.time()
        cache = cls._cache['all_settings']
        if cache['data'] is not None and (now - cache['timestamp']) < cls.CACHE_TTL:
            return cache['data']
        return None

    @classmethod
    def _set_cached_all_settings(cls, data: Dict[str, Any]):
        cls._cache['all_settings'] = {
            'data': data,
            'timestamp': time.time()
        }

    @classmethod
    def _get_cached_setting(cls, key: str) -> Optional[Any]:
        now = time.time()
        cache = cls._cache['single_setting']
        if key in cache:
            entry = cache[key]
            if (now - entry['timestamp']) < cls.CACHE_TTL:
                return entry['value']
        return None

    @classmethod
    def _set_cached_setting(cls, key: str, value: Any):
        cls._cache['single_setting'][key] = {
            'value': value,
            'timestamp': time.time()
        }

    @classmethod
    def clear_cache(cls):
        cls._cache['all_settings'] = {'data': None, 'timestamp': 0}
        cls._cache['single_setting'] = {}

    @staticmethod
    def get_all_settings(as_dict: bool = True):
        cached = SettingsService._get_cached_all_settings()
        if cached is not None:
            return cached if as_dict else SystemSetting.query.all()

        settings = SystemSetting.query.all()
        result = {}

        for key, default_value in SettingsService.DEFAULT_SETTINGS.items():
            result[key] = default_value

        for setting in settings:
            result[setting.key] = _convert_setting_value(setting.value)

        SettingsService._set_cached_all_settings(result)
        return result if as_dict else settings

    @staticmethod
    def get_setting(key: str, default: Any = None) -> Any:
        cached = SettingsService._get_cached_setting(key)
        if cached is not None:
            return cached

        setting = SystemSetting.query.filter_by(key=key).first()
        if not setting:
            return SettingsService.DEFAULT_SETTINGS.get(key, default)

        result = _convert_setting_value(setting.value)

        SettingsService._set_cached_setting(key, result)
        return result

    @staticmethod
    def save_setting(key: str, value: Any, description: Optional[str] = None) -> SystemSetting:
        setting = SystemSetting.query.filter_by(key=key).first()
        value_str = str(value).strip()

        if setting:
            setting.value = value_str
            if description is not None:
                setting.description = description.strip()
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSetting(
                key=key,
                value=value_str,
                description=description or f"系统设置 - {key}",
                updated_at=datetime.utcnow()
            )
            db.session.add(setting)

        db.session.commit()
        SettingsService.clear_cache()
        current_app.logger.info(f"系统设置更新: {key} = {value_str}")
        return setting

    @staticmethod
    def save_settings_bulk(settings_dict: Dict[str, Any]) -> int:
        updated_count = 0
        for key, value in settings_dict.items():
            if key in SettingsService.DEFAULT_SETTINGS or SystemSetting.query.filter_by(key=key).first():
                # 特殊处理多选字段
                if key == 'web_watermark_content' and isinstance(value, list):
                    value_str = ','.join(value)
                else:
                    value_str = str(value).strip()
                
                setting = SystemSetting.query.filter_by(key=key).first()
                
                if setting:
                    setting.value = value_str
                    setting.updated_at = datetime.utcnow()
                else:
                    setting = SystemSetting(
                        key=key,
                        value=value_str,
                        description=f"系统设置 - {key}",
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(setting)
                updated_count += 1
        
        if updated_count > 0:
            db.session.commit()
            SettingsService.clear_cache()
        current_app.logger.info(f"批量更新系统设置完成，共 {updated_count} 项")
        return updated_count

    @staticmethod
    def reset_to_default(key: Optional[str] = None) -> int:
        reset_count = 0
        if key:
            if key in SettingsService.DEFAULT_SETTINGS:
                SettingsService.save_setting(key, SettingsService.DEFAULT_SETTINGS[key])
                reset_count = 1
        else:
            for key, default_value in SettingsService.DEFAULT_SETTINGS.items():
                SettingsService.save_setting(key, default_value)
                reset_count += 1
        current_app.logger.warning(f"系统设置已重置为默认值，共 {reset_count} 项")
        return reset_count
