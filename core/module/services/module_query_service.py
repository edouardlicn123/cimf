import logging

from core.module.models import Module

logger = logging.getLogger(__name__)


class ModuleQueryService:
    @classmethod
    def get_frontpage_modules(cls) -> list[dict]:
        result = []
        try:
            active_modules = Module.objects.filter(is_active=True)
            for node_module in active_modules:
                from core.module.services.module_scan_service import ModuleScanService  # noqa: PLC0415

                mod_info = ModuleScanService.load_module_info(node_module.path)
                if mod_info and mod_info.get("frontpage_card", False) and "dashboard_cards" in mod_info:
                    result.append(
                        {
                            "id": node_module.module_id,
                            "name": mod_info.get("name", node_module.module_id),
                            "icon": mod_info.get("icon", "bi-grid"),
                            "module_type": node_module.module_type,
                            "clickable": mod_info.get("frontpage_card_clickable", True),
                            "dashboard_cards": mod_info.get("dashboard_cards", []),
                            "dashboard_stats": mod_info.get("dashboard_stats", False),
                        }
                    )
        except Exception as e:
            logger.warning("加载首页卡片模块失败: %s", e, exc_info=True)
        return result

    @classmethod
    def get_all(cls) -> list[Module]:
        return list(Module.objects.all())

    @classmethod
    def get_installed(cls) -> list[Module]:
        return list(Module.objects.filter(is_installed=True))

    @classmethod
    def get_active(cls, module_type: str | None = None) -> list[Module]:
        """获取已安装并激活的模块列表，可选按类型筛选"""
        qs = Module.objects.filter(is_installed=True, is_active=True)
        if module_type:
            qs = qs.filter(module_type=module_type)
        return list(qs)

    @classmethod
    def get_by_id(cls, module_id: str) -> Module | None:
        return Module.objects.filter(module_id=module_id).first()
