from core.module.services.module_dependency_service import ModuleDependencyService
from core.module.services.module_registry_service import ModuleRegistryService
from core.module.services.module_taxonomy_service import ModuleTaxonomyService


class ModuleService(
    ModuleDependencyService,
    ModuleRegistryService,
    ModuleTaxonomyService,
):
    """聚合 3 个子服务，通过多继承暴露统一接口。

    ModuleDependencyService — 模块依赖解析
    ModuleRegistryService  — 模块扫描、注册、安装、生命周期
    ModuleTaxonomyService  — 模块分类同步
    """
