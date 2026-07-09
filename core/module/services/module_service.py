from core.module.services.module_dependency_service import ModuleDependencyService
from core.module.services.module_install_service import ModuleInstallService
from core.module.services.module_lifecycle_service import ModuleLifecycleService
from core.module.services.module_query_service import ModuleQueryService
from core.module.services.module_scaffold_service import ModuleScaffoldService
from core.module.services.module_scan_service import ModuleScanService
from core.module.services.module_taxonomy_service import ModuleTaxonomyService


class ModuleService(
    ModuleDependencyService,
    ModuleScanService,
    ModuleInstallService,
    ModuleLifecycleService,
    ModuleQueryService,
    ModuleScaffoldService,
    ModuleTaxonomyService,
):
    """聚合 7 个子服务，通过多继承暴露统一接口。

    ModuleDependencyService  — 模块依赖解析
    ModuleScanService       — 模块扫描与注册
    ModuleInstallService    — 模块安装与迁移
    ModuleLifecycleService  — 生命周期管理（启用/禁用）
    ModuleQueryService      — 模块查询
    ModuleScaffoldService   — 模块脚手架
    ModuleTaxonomyService   — 模块分类同步
    """
