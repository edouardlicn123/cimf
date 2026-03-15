# -*- coding: utf-8 -*-
"""
================================================================================
文件：app/services/core/settings_service.py
路径：/home/edo/cimf-v2/app/services/core/settings_service.py
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
    - 事务安全：保存操作使用数据库事务，确保数据一致性

用法：
    1. 读取单个设置：
        value = SettingsService.get_setting('system_name')
    
    2. 读取所有设置：
        settings = SettingsService.get_all_settings()
    
    3. 保存设置：
        SettingsService.save_setting('system_name', '新名称')
    
    4. 批量保存：
        SettingsService.save_settings_bulk({'key1': 'value1', 'key2': 'value2'})
    
    5. 重置为默认值：
        SettingsService.reset_to_default()  # 重置所有
        SettingsService.reset_to_default('system_name')  # 重置单个

版本：
    - 1.0: 初始版本
    - 1.1: 添加缓存机制
    - 1.2: 优化类型转换，提取公共方法
    - 1.3: 优化多选字段处理

依赖：
    - SystemSetting: 系统设置数据模型
    - flask.current_app: 日志记录
    - app.db: 数据库会话
"""

import time
from typing import Dict, Any, Optional, Union
from flask import current_app
from app import db
from app.models import SystemSetting
from datetime import datetime


# =============================================================================
# 工具函数
# =============================================================================

def _convert_setting_value(value: str) -> Union[bool, int, float, str]:
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


# =============================================================================
# SettingsService 类
# =============================================================================

class SettingsService:
    """
    系统设置服务类
    
    说明：
        负责所有与系统配置相关的操作，是设置数据访问的唯一入口。
        路由层和业务层不应直接操作 SystemSetting 模型或 db.session。
    
    类属性：
        DEFAULT_SETTINGS: Dict[str, str] - 默认设置项和值
        _cache: Dict - 内存缓存
        CACHE_TTL: int - 缓存过期时间（秒）
    
    方法：
        get_all_settings(): 获取所有设置
        get_setting(): 获取单个设置
        save_setting(): 保存单个设置
        save_settings_bulk(): 批量保存设置
        reset_to_default(): 重置为默认值
        clear_cache(): 清除缓存
    """

    # -------------------------------------------------------------------------
    # 默认设置
    # -------------------------------------------------------------------------
    
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
    """系统默认设置项和值"""

    # -------------------------------------------------------------------------
    # 缓存管理
    # -------------------------------------------------------------------------

    _cache = {
        'all_settings': {'data': None, 'timestamp': 0},
        'single_setting': {},
    }
    """内存缓存"""
    
    CACHE_TTL = 60
    """缓存有效期（秒）"""

    @classmethod
    def _get_cached_all_settings(cls) -> Optional[Dict[str, Any]]:
        """获取缓存的所有设置"""
        now = time.time()
        cache = cls._cache['all_settings']
        if cache['data'] is not None and (now - cache['timestamp']) < cls.CACHE_TTL:
            return cache['data']
        return None

    @classmethod
    def _set_cached_all_settings(cls, data: Dict[str, Any]):
        """设置缓存的所有设置"""
        cls._cache['all_settings'] = {
            'data': data,
            'timestamp': time.time()
        }

    @classmethod
    def _get_cached_setting(cls, key: str) -> Optional[Any]:
        """获取缓存的单个设置"""
        now = time.time()
        cache = cls._cache['single_setting']
        if key in cache:
            entry = cache[key]
            if (now - entry['timestamp']) < cls.CACHE_TTL:
                return entry['value']
        return None

    @classmethod
    def _set_cached_setting(cls, key: str, value: Any):
        """设置缓存的单个设置"""
        cls._cache['single_setting'][key] = {
            'value': value,
            'timestamp': time.time()
        }

    @classmethod
    def clear_cache(cls):
        """
        清除所有缓存
        
        说明：
            在保存设置后必须调用此方法清除缓存，
            否则读取到的可能是旧的缓存值。
        """
        cls._cache['all_settings'] = {'data': None, 'timestamp': 0}
        cls._cache['single_setting'] = {}

    # -------------------------------------------------------------------------
    # 读取设置
    # -------------------------------------------------------------------------

    @staticmethod
    def get_all_settings(as_dict: bool = True):
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
        cached = SettingsService._get_cached_all_settings()
        if cached is not None:
            return cached if as_dict else SystemSetting.query.all()

        settings = SystemSetting.query.all()
        result = {}

        # 先填充默认值
        for key, default_value in SettingsService.DEFAULT_SETTINGS.items():
            result[key] = default_value

        # 用数据库值覆盖默认值
        for setting in settings:
            result[setting.key] = _convert_setting_value(setting.value)

        SettingsService._set_cached_all_settings(result)
        return result if as_dict else settings

    @staticmethod
    def get_setting(key: str, default: Any = None) -> Any:
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
        # 尝试从缓存读取
        cached = SettingsService._get_cached_setting(key)
        if cached is not None:
            return cached

        # 从数据库读取
        setting = SystemSetting.query.filter_by(key=key).first()
        if not setting:
            return SettingsService.DEFAULT_SETTINGS.get(key, default)

        # 类型转换并缓存
        result = _convert_setting_value(setting.value)
        SettingsService._set_cached_setting(key, result)
        return result

    # -------------------------------------------------------------------------
    # 保存设置
    # -------------------------------------------------------------------------

    @staticmethod
    def _save_setting_to_db(key: str, value_str: str, description: str = None):
        """
        保存设置到数据库（内部方法）
        
        说明：
            此方法是 save_setting 和 save_settings_bulk 的公共部分，
            负责实际的数据库操作。
        
        参数：
            key: 设置项的 key
            value_str: 字符串形式的值
            description: 设置描述（可选）
            
        返回：
            SystemSetting 模型实例
        """
        setting = SystemSetting.query.filter_by(key=key).first()
        
        if setting:
            setting.value = value_str
            if description:
                setting.description = description
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSetting(
                key=key,
                value=value_str,
                description=description or f"系统设置 - {key}",
                updated_at=datetime.utcnow()
            )
            db.session.add(setting)
        
        return setting

    @staticmethod
    def save_setting(key: str, value: Any, description: Optional[str] = None):
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
        setting = SettingsService._save_setting_to_db(key, value_str, description)
        
        db.session.commit()
        SettingsService.clear_cache()
        current_app.logger.info(f"系统设置更新: {key} = {value_str}")
        return setting

    @staticmethod
    def save_settings_bulk(settings_dict: Dict[str, Any]) -> int:
        """
        批量保存系统设置
        
        说明：
            批量保存多个设置项，最后统一提交事务并清除缓存。
            特殊处理 web_watermark_content 多选字段（接受列表）。
        
        参数：
            settings_dict: 设置字典
            
        返回：
            保存的设置项数量
        """
        updated_count = 0
        for key, value in settings_dict.items():
            # 检查是否是有效的设置项
            if key in SettingsService.DEFAULT_SETTINGS or SystemSetting.query.filter_by(key=key).first():
                # 特殊处理多选字段
                if key == 'web_watermark_content' and isinstance(value, list):
                    value_str = ','.join(value)
                else:
                    value_str = str(value).strip()
                
                SettingsService._save_setting_to_db(key, value_str)
                updated_count += 1
        
        # 统一提交和清除缓存
        if updated_count > 0:
            db.session.commit()
            SettingsService.clear_cache()
        current_app.logger.info(f"批量更新系统设置完成，共 {updated_count} 项")
        return updated_count

    # -------------------------------------------------------------------------
    # 重置设置
    # -------------------------------------------------------------------------

    @staticmethod
    def reset_to_default(key: Optional[str] = None) -> int:
        """
        重置设置为默认值
        
        说明：
            将指定设置项或所有设置项重置为默认值。
        
        参数：
            key: 要重置的设置 key，None 表示重置所有
            
        返回：
            重置的设置项数量
        """
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
