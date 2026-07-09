import logging
from typing import Any

from core.module.services.module_install_service import ModuleInstallService as _Install
from core.module.services.module_lifecycle_service import ModuleLifecycleService as _Lifecycle
from core.module.services.module_query_service import ModuleQueryService as _Query
from core.module.services.module_scaffold_service import ModuleScaffoldService as _Scaffold
from core.module.services.module_scan_service import ModuleScanService as _Scan

logger = logging.getLogger(__name__)


class ModuleRegistryService:
    MODULES_DIR = "modules"
    _module_info_cache: dict[str, dict[str, Any]] = {}

    MIGRATION_SCRIPT_TEMPLATE = _Install.MIGRATION_SCRIPT_TEMPLATE
    MAKEMIGRATIONS_SCRIPT_TEMPLATE = _Install.MAKEMIGRATIONS_SCRIPT_TEMPLATE

    scan_modules = _Scan.scan_modules
    scan_register_install = _Scan.scan_register_install
    scan_and_register_modules = _Scan.scan_and_register_modules
    load_module_info = _Scan.load_module_info
    _load_module_info = _Scan.load_module_info
    register_module = _Scan.register_module
    auto_register_missing = _Scan.auto_register_missing

    _check_tables_exist = _Install._check_tables_exist
    _run_migration_subprocess = _Install._run_migration_subprocess
    _install_requirements = _Install._install_requirements
    _verify_model_tables = _Install._verify_model_tables
    install_module = _Install.install_module
    _init_module_sample_data = _Install._init_module_sample_data
    register_and_install = _Install.register_and_install

    _handle_cron_tasks = _Lifecycle._handle_cron_tasks
    _update_type_active_status = _Lifecycle._update_type_active_status
    enable_module = _Lifecycle.enable_module
    disable_module = _Lifecycle.disable_module
    cleanup_uninstalled_modules = _Lifecycle.cleanup_uninstalled_modules

    get_frontpage_modules = _Query.get_frontpage_modules
    get_all = _Query.get_all
    get_installed = _Query.get_installed
    get_active = _Query.get_active
    get_by_id = _Query.get_by_id

    _sync_type = _Scaffold._sync_type
    sync_node_type = _Scaffold.sync_node_type
    sync_tool_type = _Scaffold.sync_tool_type
    create_module = _Scaffold.create_module
