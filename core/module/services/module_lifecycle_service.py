import logging
from pathlib import Path

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from core.module.models import Module, ToolType
from core.node.models import NodeType

logger = logging.getLogger(__name__)


class ModuleLifecycleService:
    MODULES_DIR = "modules"

    @classmethod
    def _handle_cron_tasks(cls, module: Module, register: bool = True) -> None:
        from core.module.services.module_scan_service import ModuleScanService  # noqa: PLC0415

        info = ModuleScanService.load_module_info(module.path) or {}
        for task_path in info.get("cron_tasks", []):
            if register:
                from core.services.cron_service import _register_single_task  # noqa: PLC0415

                _register_single_task(task_path)
            else:
                from core.services.cron_service import _unregister_single_task  # noqa: PLC0415

                _unregister_single_task(task_path)

    @classmethod
    def _update_type_active_status(cls, module: Module, is_active: bool) -> bool:
        if module.module_type == "node":
            type_obj = NodeType.objects.filter(slug=module.module_id).first()
            if not type_obj:
                logger.warning(f"节点类型未找到: {module.module_id}")
                return False
            type_obj.is_active = is_active
            type_obj.save(update_fields=["is_active"])
        elif module.module_type == "tool":
            type_obj = ToolType.objects.filter(slug=module.module_id).first()
            if not type_obj:
                logger.warning(f"工具类型未找到: {module.module_id}")
                return False
            type_obj.is_active = is_active
            type_obj.save(update_fields=["is_active"])
        return True

    @classmethod
    def enable_module(cls, module_id: str) -> Module | None:
        try:
            module = Module.objects.get(module_id=module_id)
        except Module.DoesNotExist:
            logger.warning(f"模块未找到: module_id={module_id}")
            return None

        with transaction.atomic():
            if module.is_installed:
                module.is_active = True
                module.activated_at = timezone.now()
                module.save(update_fields=["is_active", "activated_at"])

                cls._handle_cron_tasks(module, register=True)

                if not cls._update_type_active_status(module, True):
                    return None

                cache.delete("modules.installed_slugs")
                return module
        return None

    @classmethod
    def disable_module(cls, module_id: str) -> Module | None:
        try:
            module = Module.objects.get(module_id=module_id)
        except Module.DoesNotExist:
            logger.warning(f"模块未找到: module_id={module_id}")
            return None

        with transaction.atomic():
            module.is_active = False
            module.save(update_fields=["is_active"])

            cls._handle_cron_tasks(module, register=False)

            if not cls._update_type_active_status(module, False):
                return None

            cache.delete("modules.installed_slugs")
            return module
        return None

    @classmethod
    def cleanup_uninstalled_modules(cls) -> list[str]:
        registered_modules = Module.objects.filter(is_installed=True)
        cleaned = []

        for module in registered_modules:
            module_path = Path(cls.MODULES_DIR) / module.path
            module_file = module_path / "module.py"

            if not module_file.exists() and not module.is_active:
                module.delete()
                cleaned.append(module.module_id)

        return cleaned
