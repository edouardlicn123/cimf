import logging

from django.apps import AppConfig
from django.db.backends.signals import connection_created

logger = logging.getLogger(__name__)


def _enable_sqlite_wal(sender, connection, **_kwargs):  # noqa: ARG001
    """SQLite 连接创建时启用 WAL 模式"""
    if connection.vendor == "sqlite":
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode=WAL")


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        logger.info("CoreConfig.ready() 被调用")
        connection_created.connect(_enable_sqlite_wal)
        # 启动时同步 SMTP 配置到 Django 运行时设置
        try:
            from core.smtp.services.smtp_service import SmtpService  # noqa: PLC0415

            SmtpService.update_django_settings()
        except Exception:
            logger.warning("SMTP 配置同步失败（数据库可能尚未就绪）")
        # Cron 服务不再在此处初始化，改为在 run.py 或 wsgi.py 中启动服务器时初始化
