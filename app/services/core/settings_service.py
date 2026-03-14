# 文件路径：app/services/settings_service.py
# 更新日期：2026-02-17
# 功能说明：系统全局设置的核心业务逻辑，包括读取所有设置、保存/更新设置项、类型转换校验、默认值处理等

from typing import Dict, Any, Optional
from flask import current_app
from app import db
from app.models import SystemSetting  # 依赖 SystemSetting 模型
from datetime import datetime


class SettingsService:
    """
    系统设置服务层
    负责所有与系统配置相关的操作，路由层不应直接操作 SystemSetting 模型或 db.session
    """

    DEFAULT_SETTINGS = {
        # 系统基本信息
        'system_name': 'CIMF',

        # 上传相关
        'upload_max_size_mb': '50',          # MB
        'upload_max_files': '20',            # 个
        'upload_allowed_extensions': 'pdf,doc,docx,xls,xlsx,jpg,png,jpeg,zip,rar',

        # 会话与安全
        'session_timeout_minutes': '30',
        'login_max_failures': '5',
        'login_lock_minutes': '30',

        # 日志与审计
        'enable_audit_log': 'true',
        'log_retention_days': '90',

        # ========== 网页水印设置 ==========
        # 基础设置
        'enable_web_watermark': 'false',        # 是否启用网页水印
        'web_watermark_content': 'username,system_name,datetime',  # 显示内容: username/system_name/datetime (多选用逗号分隔)
        'web_watermark_opacity': '0.15',     # 透明度: 0.1-0.5
        # 防护设置
        'enable_watermark_console_detection': 'false',  # 检测控制台打开
        'enable_watermark_shortcut_block': 'false',     # 禁用快捷键
        # 导出文件水印
        'enable_export_watermark': 'false',    # 导出文件是否加水印

        # ========== 导出报表水印(原有) ==========
        'report_watermark_text': 'CIMF - 内部使用',
        'report_watermark_opacity': '0.3',

        # 其他全局开关
        'maintenance_mode': 'false',
        'allow_registration': 'false',
    }

    @staticmethod
    def get_all_settings(as_dict: bool = True) -> Dict[str, Any]:
        settings = SystemSetting.query.all()
        result = {}

        # 先填充默认值
        for key, default_value in SettingsService.DEFAULT_SETTINGS.items():
            result[key] = default_value

        # 覆盖数据库值，并做类型转换
        for setting in settings:
            value = setting.value.strip()
            if value.lower() in ('true', 'false'):
                result[setting.key] = value.lower() == 'true'
            elif value.isdigit():
                result[setting.key] = int(value)
            elif '.' in value and value.replace('.', '').isdigit():
                result[setting.key] = float(value)
            else:
                result[setting.key] = value

        return result if as_dict else settings

    @staticmethod
    def get_setting(key: str, default: Any = None) -> Any:
        setting = SystemSetting.query.filter_by(key=key).first()
        if not setting:
            return SettingsService.DEFAULT_SETTINGS.get(key, default)

        value = setting.value.strip()
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        elif value.isdigit():
            return int(value)
        elif '.' in value and value.replace('.', '').isdigit():
            return float(value)
        return value

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
        current_app.logger.info(f"系统设置更新: {key} = {value_str}")
        return setting

    @staticmethod
    def save_settings_bulk(settings_dict: Dict[str, Any]) -> int:
        updated_count = 0
        for key, value in settings_dict.items():
            if key in SettingsService.DEFAULT_SETTINGS or SystemSetting.query.filter_by(key=key).first():
                SettingsService.save_setting(key, value)
                updated_count += 1
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
