from core.module.services.module_dependency_service import ModuleDependencyService
from core.module.services.module_registry_service import ModuleRegistryService
from core.module.services.module_taxonomy_service import ModuleTaxonomyService


class ModuleService(
    ModuleDependencyService,
    ModuleRegistryService,
    ModuleTaxonomyService,
):
    pass
