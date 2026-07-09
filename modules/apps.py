import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class NodesConfig(AppConfig):
    name = "modules"

    def ready(self):
        try:
            from core.module.services import ModuleRegistryService  # noqa: PLC0415

            result = ModuleRegistryService.auto_register_missing()
            if result.get("registered", 0) > 0:
                logger.info(
                    f"自动注册完成: 新增 {result['registered']} 个模块, "
                    f"安装 {result['installed']} 个, "
                    f"跳过 {result['skipped']} 个"
                )
        except Exception:
            logger.debug("模块自动注册跳过（数据库尚未就绪）")
