import ast
import logging
import shutil
import subprocess
import sys
import tempfile
from importlib import import_module
from pathlib import Path
from typing import Any

from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.db import connection, transaction
from django.utils import timezone

from core.module.models import Module, ToolType
from core.node.models import NodeType

logger = logging.getLogger(__name__)


class ModuleRegistryService:
    MODULES_DIR = "modules"
    _module_info_cache: dict[str, dict[str, Any]] = {}

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

    @staticmethod
    def scan_modules() -> list[dict[str, Any]]:
        modules = []
        base_path = ModuleRegistryService.MODULES_DIR

        if not Path(base_path).exists():
            return modules

        module_infos = []
        for item_path in Path(base_path).iterdir():
            if not item_path.is_dir():
                continue

            module_file = item_path / "module.py"
            if not module_file.exists():
                continue

            item = item_path.name
            module_info = ModuleRegistryService._load_module_info(item)
            if module_info:
                module_info["path"] = item
                module_infos.append(module_info)

        if module_infos:
            module_ids = [m["id"] for m in module_infos]
            registered_modules = {m.module_id: m for m in Module.objects.filter(module_id__in=module_ids)}

            for module_info in module_infos:
                registered = registered_modules.get(module_info["id"])
                module_info["is_registered"] = registered is not None
                module_info["is_installed"] = registered.is_installed if registered else False
                module_info["is_active"] = registered.is_active if registered else False
                modules.append(module_info)

        return modules

    @staticmethod
    def scan_register_install(
        do_install: bool = True, dry_run: bool = False, respect_install_on_init: bool = True
    ) -> dict[str, Any]:
        all_modules = ModuleRegistryService.scan_modules()

        result = {
            "registered": 0,
            "installed": 0,
            "skipped": 0,
            "failed": [],
            "skipped_modules": [],
        }

        if dry_run:
            result["message"] = "[模拟] 将处理模块"
            return result

        pending = [m for m in all_modules if not m.get("is_registered") or not m.get("is_installed", False)]

        original_skipped = len(all_modules) - len(pending)

        skipped_due_to_install_on_init = 0
        if respect_install_on_init:
            filtered_pending = []
            for m in pending:
                if m.get("is_registered"):
                    module_obj = Module.objects.filter(module_id=m["id"]).first()
                    if not module_obj:
                        logger.warning(f"模块已注册但数据库无记录: {m['id']}")
                        continue
                    new_value = m.get("install_on_init", True)
                    if module_obj.install_on_init != new_value:
                        module_obj.install_on_init = new_value
                        module_obj.save(update_fields=["install_on_init"])
                    install_on_init = module_obj.install_on_init
                else:
                    install_on_init = m.get("install_on_init", True)

                if isinstance(install_on_init, str):
                    install_on_init = install_on_init.lower() not in ("false", "0", "no", "")
                if not install_on_init:
                    skipped_due_to_install_on_init += 1
                    result["skipped_modules"].append(m.get("name", m["id"]))
                else:
                    filtered_pending.append(m)
            pending = filtered_pending

        result["skipped"] = original_skipped + skipped_due_to_install_on_init

        for m in pending:
            try:
                module = ModuleRegistryService.register_module(m)
                result["registered"] += 1

                if do_install and not module.is_installed:
                    ok, msg = ModuleRegistryService.install_module(m["id"])
                    if ok:
                        result["installed"] += 1
                    else:
                        result["failed"].append(f"{m.get('name', m['id'])}: {msg}")
            except Exception as e:
                result["failed"].append(f"{m.get('name', m['id'])}: {e!s}")

        return result

    @staticmethod
    def scan_and_register_modules() -> list[Module]:
        ModuleRegistryService.scan_register_install(do_install=True, dry_run=False)

        registered = Module.objects.filter(is_installed=True)
        return list(registered)

    @staticmethod
    def load_module_info(module_dir: str) -> dict[str, Any] | None:
        return ModuleRegistryService._load_module_info(module_dir)

    @staticmethod
    def _load_module_info(module_dir: str) -> dict[str, Any] | None:
        if module_dir in ModuleRegistryService._module_info_cache:
            return ModuleRegistryService._module_info_cache[module_dir]

        def parse_node(node):
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Str):
                return node.s
            elif isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.NameConstant):
                return node.value
            elif isinstance(node, ast.List):
                return [parse_node(elem) for elem in node.elts]
            elif isinstance(node, ast.Dict):
                result = {}
                for k, v in zip(node.keys, node.values, strict=False):
                    key = parse_node(k)
                    value = parse_node(v)
                    if key is not None:
                        result[key] = value
                return result
            else:
                return None

        try:
            module_file = Path(ModuleRegistryService.MODULES_DIR) / module_dir / "module.py"

            with module_file.open(encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if (
                            isinstance(target, ast.Name)
                            and target.id == "MODULE_INFO"
                            and isinstance(node.value, ast.Dict)
                        ):
                            module_info = parse_node(node.value)

                            if not isinstance(module_info, dict):
                                return None

                            if "id" not in module_info:
                                raise ValueError(f"模块 {module_dir} 缺少 id 字段")
                            if "type" not in module_info:
                                raise ValueError(f"模块 {module_dir} 缺少 type 字段")

                            ModuleRegistryService._module_info_cache[module_dir] = module_info
                            return module_info

            return None

        except ValueError:
            raise
        except Exception as e:
            logger.warning(f"解析模块 {module_dir} 信息失败: {e}")
            return None

    @staticmethod
    def register_module(module_info: dict[str, Any]) -> Module:
        module_id = module_info["id"]
        existing = Module.objects.filter(module_id=module_id).first()

        if existing:
            new_version = module_info.get("version")
            if new_version and new_version != existing.version:
                logger.info("更新模块版本 %s: %s -> %s", module_id, existing.version, new_version)
                existing.name = module_info.get("name", existing.name)
                existing.version = new_version
                existing.description = module_info.get("description", existing.description)
                existing.icon = module_info.get("icon", existing.icon)
                existing.save()
            return existing

        module = Module.objects.create(
            module_id=module_id,
            name=module_info.get("name", module_id),
            version=module_info.get("version", "1.0.0"),
            author=module_info.get("author"),
            description=module_info.get("description"),
            icon=module_info.get("icon", "bi-wrench"),
            path=module_info.get("path", module_id),
            module_type=module_info.get("type", "node"),
            install_on_init=module_info.get("install_on_init", True),
            is_installed=False,
            is_active=False,
            is_system=False,
        )

        return module

    @staticmethod
    def _check_tables_exist(module_id: str) -> bool:
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

    @staticmethod
    def _run_migration_subprocess(module_id: str, _app_name: str) -> list:
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
            script_content = ModuleRegistryService.MIGRATION_SCRIPT_TEMPLATE.format(
                base_dir=repr(base_dir), module_id=repr(module_id)
            )
        else:
            script_content = ModuleRegistryService.MAKEMIGRATIONS_SCRIPT_TEMPLATE.format(
                base_dir=repr(base_dir), module_id=repr(module_id)
            )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(script_content)
            script_path = f.name

        try:
            result = subprocess.run(
                [venv_python, script_path], capture_output=True, text=True, timeout=120, check=False
            )
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                if "ERROR:" in error_msg:
                    error_msg = error_msg.split("ERROR:")[1].strip()
                errors.append(f"migrate 失败: {error_msg}")
        except subprocess.TimeoutExpired:
            errors.append("migrate 超时")
        except Exception as e:
            errors.append(f"migrate 执行失败: {e}")
        finally:
            Path(script_path).unlink()

        return errors

    @staticmethod
    def _install_requirements(module_id: str) -> tuple[bool, str]:
        req_path = Path(ModuleRegistryService.MODULES_DIR) / module_id / "requirements.txt"
        if not req_path.exists():
            return True, "无依赖需求"
        try:
            result = subprocess.run(
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
            return False, f"依赖安装异常: {e!s}"

    @staticmethod
    def _verify_model_tables(module_id: str, module_info: dict | None) -> str | None:
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

    @staticmethod
    def install_module(module_id: str) -> tuple:
        module = Module.objects.filter(module_id=module_id).first()
        if not module:
            return False, f"模块不存在: {module_id}"

        module_path = Path(ModuleRegistryService.MODULES_DIR) / module_id
        if not module_path.exists():
            return False, f"模块目录不存在: {module_id}"

        if module.is_installed:
            return True, "模块已安装"

        success, msg = ModuleRegistryService._install_requirements(module_id)
        if not success:
            return False, f"模块 {module_id} 依赖安装失败: {msg}"

        module_info = ModuleRegistryService._load_module_info(module.path)

        app_name = f"modules.{module_id}"

        models_path = module_path / "models.py"
        has_models = models_path.exists()

        if has_models:
            migration_errors = ModuleRegistryService._run_migration_subprocess(module_id, app_name)
            if migration_errors:
                error_msg = "; ".join(migration_errors)
                return False, f"模块 {module_id} 安装失败: {error_msg}"

            if not ModuleRegistryService._check_tables_exist(module_id):
                return False, f"迁移后表仍未创建，模块 {module_id} 可能配置不正确"

        err = ModuleRegistryService._verify_model_tables(module_id, module_info)
        if err:
            return False, err

        if module.module_type == "node":
            ModuleRegistryService.sync_node_type(module)
        elif module.module_type == "tool":
            ModuleRegistryService.sync_tool_type(module)

        try:
            has_taxonomies_config = module_info and module_info.get("taxonomies")
            from core.module.services.module_taxonomy_service import ModuleTaxonomyService  # noqa: PLC0415
            created_count = ModuleTaxonomyService.create_module_taxonomies(module)
            if has_taxonomies_config and created_count == 0:
                logger.warning(f"模块 {module_id} 未创建任何词汇表（可能已存在）")
        except Exception as e:
            logger.error(f"模块 {module_id} 词汇表创建失败: {e!s}")
            return (False, f"词汇表创建失败: {e!s}")

        ModuleRegistryService._init_module_sample_data(module_id)

        module.is_installed = True
        module.installed_at = timezone.now()
        module.save()

        try:
            ModuleRegistryService._handle_cron_tasks(module, register=True)
        except Exception as e:
            return False, f"cron 任务注册失败: {e}"

        return True, "安装成功"

    @staticmethod
    def _init_module_sample_data(module_id: str) -> bool:
        try:
            module_services = import_module(f"modules.{module_id}.services")
            init_func = getattr(module_services, "init_sample_data", None)
            if init_func and callable(init_func):
                init_func()
                return True
        except (ImportError, ModuleNotFoundError):
            logger.debug("模块 %s 无 services 模块或服务未实现，跳过样本数据", module_id)
        except Exception as e:
            logger.warning("初始化模块 %s 样本数据失败: %s", module_id, e)
        return False

    @staticmethod
    def register_and_install(module_info: dict[str, Any]) -> Module:
        module = ModuleRegistryService.register_module(module_info)
        if module:
            if not module.is_installed:
                success, msg = ModuleRegistryService.install_module(module_info["id"])
                if not success:
                    logger.error(f"模块 {module_info['id']} 安装失败: {msg}")
                    raise RuntimeError(f"模块 {module_info['id']} 安装失败: {msg}")
            if not module.is_active:
                ModuleRegistryService.enable_module(module_info["id"])
        return module

    @staticmethod
    def get_frontpage_modules() -> list[dict]:
        result = []
        try:
            active_modules = Module.objects.filter(is_active=True)
            for node_module in active_modules:
                mod_info = ModuleRegistryService.load_module_info(node_module.path)
                if mod_info and mod_info.get("frontpage_card", False) and "dashboard_cards" in mod_info:
                    result.append({
                        "id": node_module.module_id,
                        "name": mod_info.get("name", node_module.module_id),
                        "icon": mod_info.get("icon", "bi-grid"),
                        "module_type": node_module.module_type,
                        "clickable": mod_info.get("frontpage_card_clickable", True),
                        "dashboard_cards": mod_info.get("dashboard_cards", []),
                        "dashboard_stats": mod_info.get("dashboard_stats", False),
                    })
        except Exception as e:
            logging.getLogger(__name__).warning(f"加载首页卡片模块失败: {e}", exc_info=True)
        return result

    @staticmethod
    def _handle_cron_tasks(module: Module, register: bool = True) -> None:
        info = ModuleRegistryService._load_module_info(module.path) or {}
        for task_path in info.get("cron_tasks", []):
            if register:
                from core.services.cron_service import _register_single_task  # noqa: PLC0415

                _register_single_task(task_path)
            else:
                from core.services.cron_service import _unregister_single_task  # noqa: PLC0415

                _unregister_single_task(task_path)

    @staticmethod
    def _update_type_active_status(module: Module, is_active: bool) -> bool:
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

    @staticmethod
    def enable_module(module_id: str) -> Module | None:
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

                ModuleRegistryService._handle_cron_tasks(module, register=True)

                if not ModuleRegistryService._update_type_active_status(module, True):
                    return None

                cache.delete("modules.installed_slugs")
                return module
        return None

    @staticmethod
    def disable_module(module_id: str) -> Module | None:
        try:
            module = Module.objects.get(module_id=module_id)
        except Module.DoesNotExist:
            logger.warning(f"模块未找到: module_id={module_id}")
            return None

        with transaction.atomic():
            module.is_active = False
            module.save(update_fields=["is_active"])

            ModuleRegistryService._handle_cron_tasks(module, register=False)

            if not ModuleRegistryService._update_type_active_status(module, False):
                return None

            cache.delete("modules.installed_slugs")
            return module
        return None

    @staticmethod
    def auto_register_missing() -> dict[str, Any]:
        """扫描 modules/ 目录，自动注册尚未注册的模块"""
        try:
            table_names = connection.introspection.table_names()
            if "modules" not in table_names:
                logger.debug("modules 表不存在，跳过自动注册")
                return {"registered": 0, "message": "数据库未就绪"}
        except Exception:
            logger.debug("数据库未就绪，跳过自动注册")
            return {"registered": 0, "message": "数据库未就绪"}

        return ModuleRegistryService.scan_register_install(
            do_install=True, dry_run=False, respect_install_on_init=True
        )

    @staticmethod
    def cleanup_uninstalled_modules() -> list[str]:
        registered_modules = Module.objects.filter(is_installed=True)
        cleaned = []

        for module in registered_modules:
            module_path = Path(ModuleRegistryService.MODULES_DIR) / module.path
            module_file = module_path / "module.py"

            if not module_file.exists() and not module.is_active:
                module.delete()
                cleaned.append(module.module_id)

        return cleaned

    @staticmethod
    def get_all() -> list[Module]:
        return list(Module.objects.all())

    @staticmethod
    def get_installed() -> list[Module]:
        return list(Module.objects.filter(is_installed=True))

    @staticmethod
    def get_active() -> list[Module]:
        return list(Module.objects.filter(is_installed=True, is_active=True))

    @staticmethod
    def get_by_id(module_id: str) -> Module | None:
        return Module.objects.filter(module_id=module_id).first()

    @staticmethod
    def _sync_type(module: Module, model_class, default_icon: str):
        module_info = ModuleRegistryService._load_module_info(module.path)
        icon = module_info.get("icon", default_icon) if module_info else default_icon

        type_obj = model_class.objects.filter(slug=module.module_id).first()

        if not type_obj:
            type_obj = model_class.objects.create(
                name=module.name,
                slug=module.module_id,
                description=module.description or "",
                icon=icon,
                is_active=module.is_active,
            )
        else:
            type_obj.name = module.name
            type_obj.description = module.description or ""
            type_obj.icon = icon
            type_obj.is_active = module.is_active
            type_obj.save()

        return type_obj

    @staticmethod
    def sync_node_type(module: Module) -> NodeType:
        return ModuleRegistryService._sync_type(module, NodeType, "bi-folder")

    @staticmethod
    def sync_tool_type(module: Module) -> ToolType:
        return ModuleRegistryService._sync_type(module, ToolType, "bi-wrench")

    @staticmethod
    def create_module(
        module_id: str,
        name: str,
        module_type: str = "node",
        description: str = "",
        icon: str = "bi-folder",
        install_on_init: bool = True,
        author: str = "",
    ) -> dict[str, Any]:
        module_path = Path(ModuleRegistryService.MODULES_DIR) / module_id

        if module_path.exists():
            return {"success": False, "error": f"模块目录已存在: {module_id}"}

        if not module_id or not module_id.replace("_", "").replace("-", "").isalnum():
            return {"success": False, "error": "模块 ID 只能包含字母、数字、下划线和连字符"}

        existing = Module.objects.filter(module_id=module_id).first()
        if existing:
            return {"success": False, "error": f"模块 ID 已注册: {module_id}"}

        try:
            module_path.mkdir(parents=True, mode=0o755)

            with (module_path / "__init__.py").open("w") as f:
                f.write("# -*- coding: utf-8 -*-\n")

            module_py_content = f"""# -*- coding: utf-8 -*-

MODULE_INFO = {{
    'id': {module_id!r},
    'name': {name!r},
    'type': {module_type!r},
    'version': '1.0.0',
    'author': {author!r},
    'description': {description!r},
    'icon': {icon!r},
    'install_on_init': {install_on_init},
}}
"""
            with (module_path / "module.py").open("w") as f:
                f.write(module_py_content)

            models_content = f"""# -*- coding: utf-8 -*-
from django.db import models


class {module_id.title().replace("-", "").replace("_", "")}Model(models.Model):
    pass
"""
            with (module_path / "models.py").open("w") as f:
                f.write(models_content)

            views_content = f"""# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


@login_required
@require_http_methods(["GET"])
def list_view(request):
    return JsonResponse({{'message': 'List view for {module_id}'}})


@login_required
@require_http_methods(["GET"])
def detail_view(request, pk):
    return JsonResponse({{'message': f'Detail view for {{pk}}'}})
"""
            with (module_path / "views.py").open("w") as f:
                f.write(views_content)

            migrations_path = module_path / "migrations"
            migrations_path.mkdir(parents=True, mode=0o755)

            with (migrations_path / "__init__.py").open("w") as f:
                f.write("# -*- coding: utf-8 -*-\n")

            return {"success": True, "module_id": module_id, "path": module_path}

        except PermissionError:
            return {"success": False, "error": "权限不足，无法创建目录"}
        except Exception as e:
            if module_path.exists():
                shutil.rmtree(module_path)
            return {"success": False, "error": f"创建模块失败: {e!s}"}
