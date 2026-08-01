import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from django.apps import apps
from django.conf import settings
from django.db import connection
from django.utils import timezone

from core.module.models import Module

logger = logging.getLogger(__name__)


class ModuleInstallService:
    MODULES_DIR = "modules"

    MIGRATION_SCRIPT_TEMPLATE = """import os
import sys
sys.path.insert(0, {base_dir!r})

os.environ['DJANGO_SETTINGS_MODULE'] = 'cimf_django.settings'

import django
django.setup()

from django.core.management import call_command
try:
    call_command('migrate', {module_id!r}, verbosity=1, interactive=False)
except Exception as e:
    print(f'ERROR: {{e}}', file=sys.stderr)
    sys.exit(1)
"""

    MAKEMIGRATIONS_SCRIPT_TEMPLATE = """import os
import sys
sys.path.insert(0, {base_dir!r})

os.environ['DJANGO_SETTINGS_MODULE'] = 'cimf_django.settings'

import django
django.setup()

from django.core.management import call_command
try:
    call_command('makemigrations', {module_id!r}, verbosity=1, interactive=False)
    call_command('migrate', {module_id!r}, verbosity=1, interactive=False)
except Exception as e:
    print(f'ERROR: {{e}}', file=sys.stderr)
    sys.exit(1)
"""

    @classmethod
    def _check_tables_exist(cls, module_id: str) -> bool:
        table_set = set(connection.introspection.table_names(connection.cursor()))

        if module_id in apps.app_configs:
            try:
                models = list(apps.get_app_config(module_id).get_models())
                if not models:
                    return True

                return all(model._meta.db_table in table_set for model in models)
            except Exception as e:
                logger.warning("检查模块 %s 表结构时出错: %s", module_id, e)
                return False

        module_prefix = f"{module_id}_"
        return any(table.startswith(module_prefix) for table in table_set)

    @classmethod
    def _run_migration_subprocess(cls, module_id: str, _app_name: str) -> list:
        errors = []

        base_dir = str(settings.BASE_DIR)
        base_path = Path(settings.BASE_DIR)
        venv_python = base_path / "venv" / "bin" / "python"

        module_path = base_path / "modules" / module_id
        migrations_path = module_path / "migrations"
        models_path = module_path / "models.py"

        has_models = models_path.exists()
        has_migrations = False

        if has_models and migrations_path.exists():
            migration_files = [
                f.name for f in migrations_path.iterdir() if f.name.startswith("0") and f.name.endswith(".py")
            ]
            has_migrations = len(migration_files) > 1 or (
                len(migration_files) == 1 and "0001_initial.py" in migration_files
            )

        if has_migrations:
            script_content = cls.MIGRATION_SCRIPT_TEMPLATE.format(base_dir=base_dir, module_id=module_id)
        else:
            script_content = cls.MAKEMIGRATIONS_SCRIPT_TEMPLATE.format(base_dir=base_dir, module_id=module_id)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(script_content)
            script_path = f.name

        try:
            subprocess_env = {**os.environ, "CIMF_MODULE_MIGRATING": "1"}
            result = subprocess.run(  # noqa: S603 — controlled module install script
                [venv_python, script_path],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
                env=subprocess_env,
            )
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                if "ERROR:" in error_msg:
                    error_msg = error_msg.split("ERROR:")[1].strip()
                errors.append(f"migrate 失败: {error_msg}")
        except subprocess.TimeoutExpired:
            errors.append("migrate 超时")
        except Exception as e:
            logger.exception("模块 %s migrate 子进程异常", module_id)
            errors.append(f"migrate 执行失败: {e}")
        finally:
            Path(script_path).unlink()

        return errors

    @classmethod
    def _install_requirements(cls, module_id: str) -> tuple[bool, str]:
        req_path = Path(cls.MODULES_DIR) / module_id / "requirements.txt"
        if not req_path.exists():
            return True, "无依赖需求"
        try:
            result = subprocess.run(  # noqa: S603 — controlled pip install
                [sys.executable, "-m", "pip", "install", "-r", str(req_path)],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            if result.returncode != 0:
                return False, f"pip 安装失败: {result.stderr.strip()}"
            logger.info(f"模块 {module_id} 依赖安装完成:\n{result.stdout}")
            return True, "依赖安装成功"
        except subprocess.TimeoutExpired:
            return False, "依赖安装超时(120s)"
        except Exception as e:
            logger.exception("模块 %s 依赖安装异常", module_id)
            return False, f"依赖安装异常: {e!s}"

    @classmethod
    def _verify_model_tables(cls, module_id: str, module_info: dict | None) -> str | None:
        if not module_info or not module_info.get("models"):
            return None

        existing_tables = set(connection.introspection.table_names())

        for model_name in module_info["models"]:
            try:
                app_label = module_id
                model = apps.get_model(app_label, model_name)
                real_table_name = model._meta.db_table

                if real_table_name not in existing_tables:
                    return f"模型 {model_name} 的表未创建（期望表名: {real_table_name}）"
            except LookupError:
                expected_table = f"{module_id}_{model_name.lower()}"
                if expected_table not in existing_tables:
                    return f"模型 {model_name} 的表未创建（期望表名: {expected_table}）"
        return None

    @classmethod
    def _init_module_sample_data(cls, module_id: str) -> bool:
        try:
            from core.module.services.module_registry_service import ModuleRegistryService  # noqa: PLC0415

            module_services = ModuleRegistryService.import_module_sub(module_id, "services")
            init_func = getattr(module_services, "init_sample_data", None)
            if init_func and callable(init_func):
                init_func()
                return True
        except (ImportError, ModuleNotFoundError):
            logger.debug("模块 %s 无 services 模块或服务未实现，跳过样本数据", module_id)
        except Exception as e:
            logger.warning("初始化模块 %s 样本数据失败: %s", module_id, e)
        return False

    @classmethod
    def install_module(cls, module_id: str) -> tuple:
        from core.module.services.module_lifecycle_service import ModuleLifecycleService  # noqa: PLC0415
        from core.module.services.module_scaffold_service import ModuleScaffoldService  # noqa: PLC0415
        from core.module.services.module_scan_service import ModuleScanService  # noqa: PLC0415

        module = Module.objects.filter(module_id=module_id).first()
        if not module:
            return False, f"模块不存在: {module_id}"

        module_path = Path(cls.MODULES_DIR) / module_id
        if not module_path.exists():
            return False, f"模块目录不存在: {module_id}"

        if module.is_installed:
            return True, "模块已安装"

        success, msg = cls._install_requirements(module_id)
        if not success:
            return False, f"模块 {module_id} 依赖安装失败: {msg}"

        module_info = ModuleScanService.load_module_info(module.path)

        app_name = f"modules.{module_id}"

        models_path = module_path / "models.py"
        has_models = models_path.exists()

        if has_models:
            if cls._check_tables_exist(module_id):
                logger.info("模块 %s 数据表已存在，跳过迁移", module_id)
            else:
                migration_errors = cls._run_migration_subprocess(module_id, app_name)
                if migration_errors:
                    error_msg = "; ".join(migration_errors)
                    return False, f"模块 {module_id} 安装失败: {error_msg}"

                if not cls._check_tables_exist(module_id):
                    return False, f"迁移后表仍未创建，模块 {module_id} 可能配置不正确"

        err = cls._verify_model_tables(module_id, module_info)
        if err:
            return False, err

        if module.module_type == "node":
            ModuleScaffoldService.sync_node_type(module)
        elif module.module_type == "tool":
            ModuleScaffoldService.sync_tool_type(module)

        try:
            has_taxonomies_config = module_info and module_info.get("taxonomies")
            from core.module.services.module_taxonomy_service import ModuleTaxonomyService  # noqa: PLC0415

            created_count = ModuleTaxonomyService.create_module_taxonomies(module)
            if has_taxonomies_config and created_count == 0:
                logger.warning(f"模块 {module_id} 未创建任何词汇表（可能已存在）")
        except Exception as e:
            logger.error(f"模块 {module_id} 词汇表创建失败: {e!s}")
            return (False, f"词汇表创建失败: {e!s}")

        cls._init_module_sample_data(module_id)

        module.is_installed = True
        module.installed_at = timezone.now()
        module.save(update_fields=["is_installed", "installed_at"])

        try:
            ModuleLifecycleService._handle_cron_tasks(module, register=True)
        except Exception as e:
            logger.exception("模块 %s cron 任务注册失败", module.module_id)
            return False, f"cron 任务注册失败: {e}"

        return True, "安装成功"

    @classmethod
    def register_and_install(cls, module_info: dict[str, Any]) -> Module:
        from core.module.services.module_lifecycle_service import ModuleLifecycleService  # noqa: PLC0415
        from core.module.services.module_scan_service import ModuleScanService  # noqa: PLC0415

        module = ModuleScanService.register_module(module_info)
        if module:
            if not module.is_installed:
                success, msg = cls.install_module(module_info["id"])
                if not success:
                    logger.error(f"模块 {module_info['id']} 安装失败: {msg}")
                    raise RuntimeError(f"模块 {module_info['id']} 安装失败: {msg}")
            if not module.is_active:
                ModuleLifecycleService.enable_module(module_info["id"])
        return module
