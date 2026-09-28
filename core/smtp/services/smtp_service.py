"""
SMTP 配置管理服务
"""

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import Any

import socks
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend

from core.services import SettingsService

logger = logging.getLogger(__name__)


def _proxy_settings(config: dict[str, Any]) -> tuple[str, int] | None:
    """返回 (proxy_host, proxy_port)，未配置代理时返回 None"""
    if not config.get("use_proxy", False):
        return None
    proxy_host = (config.get("proxy_host") or "").strip()
    if not proxy_host:
        return None
    return proxy_host, int(config.get("proxy_port", 10808))


def _open_socks_socket(proxy_host: str, proxy_port: int, host: str, port: int, timeout, context):
    """经 SOCKS5 代理建立到 host:port 的连接（仅作用于本连接）"""
    sock = socks.socksocket()
    sock.set_proxy(socks.SOCKS5, proxy_host, proxy_port)
    sock.settimeout(timeout)
    try:
        if context is not None:
            sock = context.wrap_socket(sock, server_hostname=host)
        sock.connect((host, port))
    # 关闭套接字后原样抛出，由调用方统一记录
    except Exception:  # noqa: CIMF_W007
        sock.close()
        logger.debug("SOCKS5 代理连接失败: %s -> %s:%s", proxy_host, host, port, exc_info=True)
        raise
    return sock


class _SocksSMTP(smtplib.SMTP):
    """走 SOCKS5 代理的 SMTP（每连接生效，不改动全局 socket）"""

    def __init__(self, host, port, *, proxy_host, proxy_port, **kwargs):
        self._proxy_host = proxy_host
        self._proxy_port = proxy_port
        super().__init__(host, port, **kwargs)

    def _get_socket(self, host, port, timeout):
        return _open_socks_socket(self._proxy_host, self._proxy_port, host, port, timeout, None)


class _SocksSMTP_SSL(smtplib.SMTP_SSL):
    """走 SOCKS5 代理的隐式 SSL SMTP（每连接生效，不改动全局 socket）"""

    def __init__(self, host, port, *, proxy_host, proxy_port, **kwargs):
        self._proxy_host = proxy_host
        self._proxy_port = proxy_port
        super().__init__(host, port, **kwargs)

    def _get_socket(self, host, port, timeout):
        return _open_socks_socket(
            self._proxy_host, self._proxy_port, host, port, timeout, getattr(self, "context", None)
        )


def _make_smtp(config: dict[str, Any], host: str, port, timeout, context):
    """按配置创建 SMTP 连接：配置代理时使用 SOCKS5 子类，否则用标准类"""
    proxy = _proxy_settings(config)
    use_ssl = config.get("use_ssl", False)
    if proxy is None:
        return smtplib.SMTP_SSL(host, port, timeout=timeout, context=context) if use_ssl \
            else smtplib.SMTP(host, port, timeout=timeout)
    proxy_host, proxy_port = proxy
    if use_ssl:
        return _SocksSMTP_SSL(host, port, timeout=timeout, context=context,
                              proxy_host=proxy_host, proxy_port=proxy_port)
    return _SocksSMTP(host, port, timeout=timeout,
                      proxy_host=proxy_host, proxy_port=proxy_port)


class ProxySmtpEmailBackend(SMTPEmailBackend):
    """支持 SOCKS5 代理的 Django 邮件后端

    只替换本后端自身的 connection_class，代理仅作用于该邮件连接，
    不会像全局猴补丁 socket.socket 那样影响进程内其它线程的网络请求。
    """

    def __init__(self, *args, proxy_host: str = "", proxy_port: int = 10808, **kwargs):
        self._proxy_host = proxy_host
        self._proxy_port = proxy_port
        super().__init__(*args, **kwargs)

    @property
    def connection_class(self):
        if self.use_ssl:
            def factory(host, port, **kwargs):
                return _SocksSMTP_SSL(
                    host, port, proxy_host=self._proxy_host,
                    proxy_port=self._proxy_port, **kwargs
                )
        else:
            def factory(host, port, **kwargs):
                return _SocksSMTP(
                    host, port, proxy_host=self._proxy_host,
                    proxy_port=self._proxy_port, **kwargs
                )
        return factory


SMTP_PRESETS = {
    "gmail_ssl": {
        "name": "Gmail (SSL)",
        "host": "smtp.gmail.com",
        "port": 465,
        "use_ssl": True,
        "use_tls": False,
        "help_text": "需要开启两步验证并生成应用专用密码",
        "help_url": "https://support.google.com/accounts/answer/185833",
    },
    "gmail_tls": {
        "name": "Gmail (TLS)",
        "host": "smtp.gmail.com",
        "port": 587,
        "use_ssl": False,
        "use_tls": True,
        "help_text": "需要开启两步验证并生成应用专用密码",
        "help_url": "https://support.google.com/accounts/answer/185833",
    },
    "163_ssl": {
        "name": "163邮箱 (SSL)",
        "host": "smtp.163.com",
        "port": 465,
        "use_ssl": True,
        "use_tls": False,
        "help_text": "需要在邮箱设置中开启SMTP服务并获取授权码",
        "help_url": None,
    },
    "163_tls": {
        "name": "163邮箱 (TLS)",
        "host": "smtp.163.com",
        "port": 587,
        "use_ssl": False,
        "use_tls": True,
        "help_text": "需要在邮箱设置中开启SMTP服务并获取授权码",
        "help_url": None,
    },
    "proton_ssl": {
        "name": "ProtonMail (SSL)",
        "host": "smtp.protonmail.com",
        "port": 465,
        "use_ssl": True,
        "use_tls": False,
        "help_text": "需要ProtonMail Bridge本地代理",
        "help_url": "https://proton.me/mail/bridge",
    },
    "proton_tls": {
        "name": "ProtonMail (TLS)",
        "host": "smtp.protonmail.com",
        "port": 587,
        "use_ssl": False,
        "use_tls": True,
        "help_text": "需要ProtonMail Bridge本地代理",
        "help_url": "https://proton.me/mail/bridge",
    },
    "custom": {
        "name": "自定义",
        "host": "",
        "port": 587,
        "use_ssl": False,
        "use_tls": True,
        "help_text": "手动填写SMTP服务器信息",
        "help_url": None,
    },
}


class SmtpService:
    """SMTP 配置管理服务"""

    @classmethod
    def get_provider_presets(cls, provider: str | None = None) -> dict[str, Any]:
        """获取服务商预设配置"""
        if provider:
            return SMTP_PRESETS.get(provider, SMTP_PRESETS["custom"])
        return SMTP_PRESETS

    @classmethod
    def get_current_config(cls) -> dict[str, Any]:
        """获取当前 SMTP 配置"""
        settings_dict = SettingsService.get_all_settings()

        config = {
            "enabled": str(settings_dict.get("smtp_enabled", "false")).lower() == "true",
            "service_connected": str(settings_dict.get("smtp_service_connected", "false")).lower() == "true",
            "provider": settings_dict.get("smtp_provider", "gmail_tls"),
            "host": settings_dict.get("smtp_host", "smtp.gmail.com"),
            "port": int(settings_dict.get("smtp_port", "587")),
            "use_ssl": str(settings_dict.get("smtp_use_ssl", "false")).lower() == "true",
            "use_tls": str(settings_dict.get("smtp_use_tls", "true")).lower() == "true",
            "username": settings_dict.get("smtp_username", ""),
            "password": cls._get_password(),
            "from_email": settings_dict.get("smtp_from_email", ""),
            "from_name": settings_dict.get("smtp_from_name", "仙芙CIMF"),
            "timeout": int(settings_dict.get("smtp_timeout", "30")),
            "skip_verify": str(settings_dict.get("smtp_skip_verify", "false")).lower() == "true",
            "batch_size": int(settings_dict.get("smtp_batch_size", "10")),
            "send_interval": int(settings_dict.get("smtp_send_interval", "240")),
            "log_days": int(settings_dict.get("smtp_log_days", "30")),
            "failed_notify": str(settings_dict.get("smtp_failed_notify", "false")).lower() == "true",
            "notify_email": settings_dict.get("smtp_notify_email", ""),
            "system_url": settings_dict.get("smtp_system_url", ""),
            "use_proxy": str(settings_dict.get("smtp_use_proxy", "false")).lower() == "true",
            "proxy_host": settings_dict.get("smtp_proxy_host", ""),
            "proxy_port": int(settings_dict.get("smtp_proxy_port", "10808")),
        }

        return config

    @classmethod
    def _get_password(cls) -> str:
        """获取 SMTP 密码，优先从环境变量读取"""
        env_password = os.environ.get("DJANGO_SMTP_PASSWORD", "")
        if env_password:
            return env_password

        settings_dict = SettingsService.get_all_settings()
        return settings_dict.get("smtp_password", "")

    @classmethod
    def save_config(cls, config: dict[str, Any]) -> None:
        """保存 SMTP 配置"""
        mappings = {
            "smtp_enabled": "true" if config.get("enabled") else "false",
            "smtp_provider": str(config.get("provider", "gmail_tls")),
            "smtp_host": str(config.get("host", "")),
            "smtp_port": str(config.get("port", "587")),
            "smtp_use_ssl": "true" if config.get("use_ssl") else "false",
            "smtp_use_tls": "true" if config.get("use_tls") else "false",
            "smtp_username": str(config.get("username", "")),
            "smtp_from_email": str(config.get("from_email", "")),
            "smtp_from_name": str(config.get("from_name", "仙芙CIMF")),
            "smtp_timeout": str(config.get("timeout", "30")),
            "smtp_skip_verify": "true" if config.get("skip_verify") else "false",
            "smtp_batch_size": str(config.get("batch_size", "10")),
            "smtp_send_interval": str(config.get("send_interval", "240")),
            "smtp_log_days": str(config.get("log_days", "30")),
            "smtp_failed_notify": "true" if config.get("failed_notify") else "false",
            "smtp_notify_email": str(config.get("notify_email", "")),
            "smtp_system_url": str(config.get("system_url", "")),
            "smtp_use_proxy": "true" if config.get("use_proxy") else "false",
            "smtp_proxy_host": str(config.get("proxy_host", "")),
            "smtp_proxy_port": str(config.get("proxy_port", "10808")),
        }

        for key, value in mappings.items():
            SettingsService.save_setting(key, value)

        # 同步开启/关闭后台邮件任务
        smtp_enabled = config.get("enabled", False)
        SettingsService.save_setting("cron_email_sending_enabled", "true" if smtp_enabled else "false")
        SettingsService.save_setting("cron_email_cleanup_enabled", "true" if smtp_enabled else "false")

        password = config.get("password", "")
        if password:
            SettingsService.save_setting("smtp_password", password)

        cls.update_django_settings()

    @classmethod
    def update_connection_status(cls, success: bool | None = None, message: str = "") -> tuple[bool, str]:
        """测试连接并存储服务状态"""
        if success is None:
            success, message = cls.test_connection()
        SettingsService.save_setting("smtp_service_connected", "true" if success else "false")
        return success, message

    @classmethod
    def test_connection(cls, config: dict[str, Any] | None = None) -> tuple[bool, str]:
        """测试 SMTP 连接"""
        if config is None:
            config = cls.get_current_config()

        try:
            password = config.get("password") or cls._get_password()
            if not password:
                return False, "请先配置 SMTP 密码"

            from_email = config.get("from_email") or config.get("username")
            if not from_email:
                return False, "请先配置发件人邮箱"

            host = config.get("host", "smtp.gmail.com")
            port = config.get("port", 587)
            timeout = config.get("timeout", 30)
            use_tls = config.get("use_tls", True)
            skip_verify = config.get("skip_verify", False)

            context = None
            if skip_verify:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

            server = _make_smtp(config, host, port, timeout, context)

            with server:
                if use_tls:
                    server.starttls(context=context)

                username = config.get("username", from_email)
                server.login(username, password)

                msg = EmailMessage()
                msg["From"] = f"{config.get('from_name', '仙芙CIMF')} <{from_email}>"
                msg["To"] = from_email
                msg["Subject"] = "CIMF 系统邮件测试"
                msg.set_content("这是一封来自 CIMF 系统的测试邮件，如果您收到此邮件，说明 SMTP 配置正确。")

                server.send_message(msg)

            return True, "连接测试成功！"

        except Exception as e:
            logger.warning(f"SMTP 连接测试失败: {e}", exc_info=True)
            return False, f"连接失败: {e!s}"

    @classmethod
    def update_django_settings(cls) -> None:
        """更新 Django 邮件配置（运行时）"""
        config = cls.get_current_config()

        if not config.get("enabled"):
            return

        proxy = _proxy_settings(config)
        if proxy is not None:
            settings.EMAIL_BACKEND = "core.smtp.services.smtp_service.ProxySmtpEmailBackend"
        else:
            settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
        settings.EMAIL_HOST = config.get("host", "smtp.gmail.com")
        settings.EMAIL_PORT = config.get("port", 587)
        settings.EMAIL_USE_TLS = config.get("use_tls", True)
        settings.EMAIL_USE_SSL = config.get("use_ssl", False)
        settings.EMAIL_HOST_USER = config.get("username", "")
        settings.EMAIL_HOST_PASSWORD = config.get("password", "")
        settings.EMAIL_TIMEOUT = config.get("timeout", 30)
        from_name = config.get("from_name", "仙芙CIMF")
        from_email = config.get("from_email", "")
        settings.DEFAULT_FROM_EMAIL = f"{from_name} <{from_email}>" if from_email else from_name

    @classmethod
    def get_system_url(cls) -> str:
        """获取配置的系统访问地址（不含末尾斜杠）"""
        config = cls.get_current_config()
        system_url = config.get("system_url", "").strip()
        return system_url.rstrip("/") if system_url else ""
