"""应用启动任务（延迟到数据库就绪后执行）

背景：
    Django 禁止在 AppConfig.ready() 中访问数据库，否则触发警告：
    RuntimeWarning: Accessing the database during app initialization is discouraged.
    原 ready() 中的 SMTP 配置同步与模块自动注册均移到本模块：

    - 显式启动路径（run.py / wsgi.py / asgi.py）在 django.setup() 后调用 init_startup_tasks()
    - 其它入口（如 manage.py runserver）通过 request_started 信号在首个请求时兜底执行

    进程内只执行一次（_startup_done 守卫），避免重复同步。
"""

import logging

logger = logging.getLogger(__name__)

_startup_done = False


def _run_startup_tasks() -> None:
    """应用就绪后的启动任务：SMTP 配置同步、模块自动注册"""
    global _startup_done
    if _startup_done:
        return
    _startup_done = True

    try:
        from core.smtp.services.smtp_service import SmtpService  # noqa: PLC0415

        SmtpService.update_django_settings()
    except Exception:
        logger.warning("SMTP 配置同步失败（数据库可能尚未就绪）")

    try:
        from core.module.services import ModuleRegistryService  # noqa: PLC0415

        result = ModuleRegistryService.auto_register_missing()
        if result.get("registered", 0) > 0:
            logger.info(
                f"自动注册完成: 新增 {result['registered']} 个模块, "
                f"安装 {result['installed']} 个, "
                f"跳过 {result['skipped']} 个"
            )
    except Exception:  # noqa: CIMF_W007 — 数据库未就绪时预期行为
        logger.debug("模块自动注册跳过（数据库尚未就绪）")


def run_startup_on_request(sender, **_kwargs):  # noqa: ARG001
    """request_started 信号处理器：非显式启动路径在首个请求时兜底执行"""
    _run_startup_tasks()


def init_startup_tasks() -> None:
    """显式启动路径（run.py / wsgi.py / asgi.py）在 django.setup() 完成后调用"""
    _run_startup_tasks()
