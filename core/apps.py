import logging

from django.apps import AppConfig
from django.core.signals import request_started
from django.db.backends.signals import connection_created

logger = logging.getLogger(__name__)


def _enable_sqlite_wal(sender, connection, **_kwargs):  # noqa: ARG001
    """SQLite 连接创建时启用 WAL 模式"""
    try:
        if connection.vendor == "sqlite":
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
    except Exception:
        logger.warning("启用 SQLite WAL 模式失败", exc_info=True)


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        logger.info("CoreConfig.ready() 被调用")
        # 显式导入 checks 模块以注册自定义 Django 检查（CIMF_W001~W007）
        from core import checks  # noqa: F401, PLC0415

        connection_created.connect(_enable_sqlite_wal, dispatch_uid="enable_sqlite_wal")
        # 启动任务（SMTP 配置同步、模块自动注册）需访问数据库，不能在 ready() 中执行。
        # 显式启动路径（run.py / wsgi.py / asgi.py）在 django.setup() 后调用
        # core.startup.init_startup_tasks()；此处注册 request_started 兜底其它入口
        # （如 manage.py runserver），避免应用初始化期间访问数据库的 RuntimeWarning。
        from core.startup import run_startup_on_request  # noqa: PLC0415

        request_started.connect(run_startup_on_request, dispatch_uid="core_run_startup_tasks")
        # Cron 服务不再在此处初始化，改为在 run.py 或 wsgi.py 中启动服务器时初始化
