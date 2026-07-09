import logging

from core.module.models import Module

logger = logging.getLogger(__name__)


class ModuleDependencyService:

    @staticmethod
    def check_dependencies(module_id: str, visited: set | None = None) -> tuple:
        if visited is None:
            visited = set()

        if module_id in visited:
            chain = " -> ".join([*list(visited), module_id])
            return False, f"发现循环依赖：{chain}", []
        visited.add(module_id)

        from core.module.services.module_registry_service import ModuleRegistryService  # noqa: PLC0415
        module_info = ModuleRegistryService.load_module_info(module_id)
        if not module_info:
            return True, "", []

        require = module_info.get("require", [])
        if not require:
            return True, "", []

        for dep_id in require:
            dep_module = Module.objects.filter(module_id=dep_id).first()

            if not dep_module:
                dep_name = module_info.get("name", dep_id)
                return False, f"需要「{dep_name}」已安装并启用（当前状态：未安装）", [dep_id]

            if not dep_module.is_installed:
                dep_name = module_info.get("name", dep_id)
                return False, f"需要「{dep_name}」已安装并启用（当前状态：未安装）", [dep_id]

            if not dep_module.is_active:
                dep_name = module_info.get("name", dep_id)
                return False, f"需要「{dep_name}」已安装并启用（当前状态：已安装但未启用）", [dep_id]

            ok, err, chain = ModuleDependencyService.check_dependencies(dep_id, visited.copy())
            if not ok:
                return False, err, [dep_id, *chain]

        return True, "", []

    @staticmethod
    def verify_dependencies(module_id: str) -> tuple:
        ok, err, chain = ModuleDependencyService.check_dependencies(module_id)
        return ok, err, chain

    @staticmethod
    def get_dependency_chain(module_id: str) -> list:
        from core.module.services.module_registry_service import ModuleRegistryService  # noqa: PLC0415

        def collect_chain(cid, visited, chain):
            if cid in visited:
                return
            visited.add(cid)

            module_info = ModuleRegistryService.load_module_info(cid)
            dep_module = Module.objects.filter(module_id=cid).first()
            if not dep_module:
                raise ValueError(
                    f"需要「{module_info.get('name', cid)}」已安装并启用（当前状态：未注册）"
                )

            info = {
                "module_id": cid,
                "name": module_info.get("name", cid) if module_info else cid,
                "status": "installed_active"
                if (dep_module and dep_module.is_installed and dep_module.is_active)
                else "installed_inactive"
                if (dep_module and dep_module.is_installed)
                else "not_installed",
            }
            chain.append(info)

            if module_info:
                for dep_id in module_info.get("require", []):
                    collect_chain(dep_id, visited, chain)

        chain = []
        collect_chain(module_id, set(), chain)
        return chain[1:] if len(chain) > 1 else []
