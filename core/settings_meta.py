"""
系统设置项元数据定义

每个设置项的定义：
    key: {"default": "默认值", "type": Python类型}

type 用于：
    - system_settings.html 模板生成表单
    - save_settings_bulk 的类型判断
"""

SETTINGS_META = {
    # ===== System =====
    "system_name": {"default": "仙芙CIMF", "type": str},
    "maintenance_mode": {"default": "false", "type": bool},
    "allow_registration": {"default": "false", "type": bool},
    # ===== Site =====
    "site_logo_enabled": {"default": "true", "type": bool},
    "site_logo_path": {"default": "", "type": str},
    # ===== Welcome =====
    "welcome_title": {"default": "欢迎！", "type": str},
    "welcome_subtitle": {"default": "让我们一起把项目完善吧。", "type": str},
    "welcome_intro": {"default": "初始用户名：admin 初始密码：admin123", "type": str},
    # ===== Upload =====
    "upload_max_size_mb": {"default": "12", "type": int},
    "upload_max_files": {"default": "20", "type": int},
    "upload_allowed_extensions": {"default": "pdf,doc,docx,xls,xlsx,jpg,png,jpeg,zip,rar", "type": str},
    # ===== Session & Login =====
    "session_timeout_minutes": {"default": "30", "type": int},
    "login_max_failures": {"default": "5", "type": int},
    "login_lock_minutes": {"default": "30", "type": int},
    # ===== Audit Log =====
    "enable_audit_log": {"default": "true", "type": bool},
    "log_retention_days": {"default": "90", "type": int},
    # ===== Watermark =====
    "enable_web_watermark": {"default": "false", "type": bool},
    "web_watermark_content": {"default": "username,system_name,datetime", "type": str},
    "web_watermark_custom_text": {"default": "自定义文字", "type": str},
    "web_watermark_opacity": {"default": "0.15", "type": float},
    "enable_watermark_console_detection": {"default": "false", "type": bool},
    "enable_watermark_shortcut_block": {"default": "false", "type": bool},
    "enable_export_watermark": {"default": "false", "type": bool},
    # ===== Time Sync =====
    "enable_time_sync": {"default": "true", "type": bool},
    "time_server_url": {"default": "https://timeapi.io/api/time/current/zone?timeZone=Asia/Shanghai", "type": str},
    "time_zone": {"default": "Asia/Shanghai", "type": str},
    "time_sync_interval": {"default": "15", "type": int},
    "time_sync_max_retries": {"default": "5", "type": int},
    "system_synced_time": {"default": "", "type": str},
    "system_sync_monotonic": {"default": "0", "type": int},
    # ===== Cron =====
    "cron_time_sync_enabled": {"default": "true", "type": bool},
    "cron_cache_cleanup_enabled": {"default": "true", "type": bool},
    "cron_email_sending_enabled": {"default": "false", "type": bool},
    "cron_email_cleanup_enabled": {"default": "false", "type": bool},
    "cron_email_cleanup_interval": {"default": "86400", "type": int},
    # ===== SMTP =====
    "smtp_enabled": {"default": "false", "type": bool},
    "smtp_provider": {"default": "gmail_tls", "type": str},
    "smtp_host": {"default": "smtp.gmail.com", "type": str},
    "smtp_port": {"default": "587", "type": int},
    "smtp_use_ssl": {"default": "false", "type": bool},
    "smtp_use_tls": {"default": "true", "type": bool},
    "smtp_username": {"default": "", "type": str},
    "smtp_from_email": {"default": "", "type": str},
    "smtp_from_name": {"default": "仙芙CIMF", "type": str},
    "smtp_timeout": {"default": "30", "type": int},
    "smtp_skip_verify": {"default": "false", "type": bool},
    "smtp_password": {"default": "", "type": str},
    "smtp_retry_count": {"default": "3", "type": int},
    "smtp_batch_size": {"default": "10", "type": int},
    "smtp_log_days": {"default": "30", "type": int},
    "smtp_failed_notify": {"default": "false", "type": bool},
    "smtp_notify_email": {"default": "", "type": str},
    "smtp_system_url": {"default": "", "type": str},
    "smtp_proxy_host": {"default": "127.0.0.1", "type": str},
    "smtp_proxy_port": {"default": "10808", "type": int},
    "smtp_use_proxy": {"default": "false", "type": bool},
    "smtp_send_interval": {"default": "240", "type": int},
}
