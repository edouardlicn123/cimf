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
from django.db import connection
from django.utils import timezone

from core.models import Taxonomy, TaxonomyItem
from core.module.models import Module, ToolType
from core.node.models import NodeType

logger = logging.getLogger(__name__)


class ModuleService:
    MODULES_DIR = "modules"
    _module_info_cache: dict[str, dict[str, Any]] = {}

    @staticmethod
    def scan_modules() -> list[dict[str, Any]]:
        modules = []
        base_path = ModuleService.MODULES_DIR

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
            module_info = ModuleService._load_module_info(item)
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
        """
        统一扫描、注册、安装流程
        Args:
            do_install: 是否执行安装（阶段4用True，仅扫描用False）
            dry_run: 是否模拟执行
            respect_install_on_init: 是否尊重install_on_init设置（初始化阶段为True，手动扫描为False）
        Returns:
            dict: {'registered': 数量, 'installed': 数量, 'skipped': 数量, 'failed': [], 'skipped_modules': []}
        """
        all_modules = ModuleService.scan_modules()

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

        # 筛选需要处理的模块：未注册 或 未安装
        pending = [m for m in all_modules if not m.get("is_registered") or not m.get("is_installed", False)]

        # 计算原始的skipped（已注册且已安装）
        original_skipped = len(all_modules) - len(pending)

        # 如果尊重install_on_init设置，过滤掉明确设置为False的模块
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
                module = ModuleService.register_module(m)
                result["registered"] += 1

                if do_install and not module.is_installed:
                    ok, msg = ModuleService.install_module(m["id"])
                    if ok:
                        result["installed"] += 1
                    else:
                        result["failed"].append(f"{m.get('name', m['id'])}: {msg}")
            except Exception as e:
                result["failed"].append(f"{m.get('name', m['id'])}: {e!s}")

        return result

    @staticmethod
    def scan_and_register_modules() -> list[Module]:
        """扫描并注册模块（供视图调用，保持原返回值类型）"""
        ModuleService.scan_register_install(do_install=True, dry_run=False)

        # 返回已安装的模块列表（保持原返回值类型）
        registered = Module.objects.filter(is_installed=True)
        return list(registered)

    @staticmethod
    def load_module_info(module_dir: str) -> dict[str, Any] | None:
        """公开方法：加载模块的 MODULE_INFO"""
        return ModuleService._load_module_info(module_dir)

    @staticmethod
    def _load_module_info(module_dir: str) -> dict[str, Any] | None:
        if module_dir in ModuleService._module_info_cache:
            return ModuleService._module_info_cache[module_dir]

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
            module_file = Path(ModuleService.MODULES_DIR) / module_dir / "module.py"

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

                            if "type" not in module_info:
                                raise ValueError(f"模块 {module_dir} 缺少 type 字段")

                            ModuleService._module_info_cache[module_dir] = module_info
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
            logger.info(f"更新现有模块: {module_id}")
            # 更新现有模块
            existing.module_type = module_info.get("type", "node")
            existing.name = module_info.get("name", existing.name)
            existing.version = module_info.get("version", existing.version)
            existing.description = module_info.get("description", existing.description)
            existing.icon = module_info.get("icon", existing.icon)
            existing.install_on_init = module_info.get("install_on_init", True)
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
            except Exception:
                pass

        module_prefix = f"{module_id}_"
        return any(table.startswith(module_prefix) for table in table_set)

    @staticmethod
    def _run_migration_subprocess(module_id: str, _app_name: str) -> list:
        """
        通过subprocess执行迁移（Django限制：无法运行时动态重初始化apps）

        注意：Django的apps系统不支持运行时动态添加应用并重新初始化
        虽然subprocess较慢（~3秒/模块），但这是目前最可靠的方法

        优化建议：合并迁移文件（./manage.py squashmigrations）可减少文件数量
        """
        errors = []

        base_dir = str(settings.BASE_DIR)
        base_path = Path(settings.BASE_DIR)
        venv_python = base_path / "venv" / "bin" / "python"

        # 检查是否有迁移文件
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
            script_content = f"""
import os
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
        else:
            script_content = f"""
import os
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
        """安装模块的 Python 依赖（requirements.txt）"""
        req_path = Path(ModuleService.MODULES_DIR) / module_id / "requirements.txt"
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
    def install_module(module_id: str) -> tuple:
        module = Module.objects.filter(module_id=module_id).first()
        if not module:
            return False, f"模块不存在: {module_id}"

        module_path = Path(ModuleService.MODULES_DIR) / module_id
        if not module_path.exists():
            return False, f"模块目录不存在: {module_id}"

        if module.is_installed:
            return True, "模块已安装"

        # 安装 Python 依赖（迁移前执行，因为 models/services 可能需要 import）
        success, msg = ModuleService._install_requirements(module_id)
        if not success:
            return False, f"模块 {module_id} 依赖安装失败: {msg}"

        # 提前加载模块信息，供后续使用
        module_info = ModuleService._load_module_info(module.path)

        app_name = f"modules.{module_id}"

        # 检查模块是否有 models.py 文件
        models_path = module_path / "models.py"
        has_models = models_path.exists()

        # 如果没有模型文件，跳过迁移步骤，直接标记为安装成功
        if not has_models:
            pass
        else:
            # 执行迁移（subprocess方式，Django限制：无法运行时动态重初始化apps）
            migration_errors = ModuleService._run_migration_subprocess(module_id, app_name)
            if migration_errors:
                error_msg = "; ".join(migration_errors)
                return False, f"模块 {module_id} 安装失败: {error_msg}"

        # 没有模型文件的模块，跳过表检查
        if not has_models:
            pass
        elif not ModuleService._check_tables_exist(module_id):
            return False, f"迁移后表仍未创建，模块 {module_id} 可能配置不正确"

        # 验证 models 字段中列出的所有模型表
        if module_info and module_info.get("models"):
            existing_tables = set(connection.introspection.table_names())

            for model_name in module_info["models"]:
                try:
                    # 使用Django的模型元数据获取真实表名
                    app_label = module_id
                    model = apps.get_model(app_label, model_name)
                    real_table_name = model._meta.db_table

                    if real_table_name not in existing_tables:
                        return False, f"模型 {model_name} 的表未创建（期望表名: {real_table_name}）"
                except LookupError:
                    # 如果找不到模型，回退到默认规则
                    expected_table = f"{module_id}_{model_name.lower()}"
                    if expected_table not in existing_tables:
                        return False, f"模型 {model_name} 的表未创建（期望表名: {expected_table}）"

        if module.module_type == "node":
            ModuleService.sync_node_type(module)
        elif module.module_type == "tool":
            ModuleService.sync_tool_type(module)

        try:
            # 检查模块是否配置了词汇表
            has_taxonomies_config = module_info and module_info.get("taxonomies")

            created_count = ModuleService.create_module_taxonomies(module)
            # 只在配置了词汇表但创建失败时才警告
            if has_taxonomies_config and created_count == 0:
                logger.warning(f"模块 {module_id} 未创建任何词汇表（可能已存在）")
        except Exception as e:
            logger.error(f"模块 {module_id} 词汇表创建失败: {e!s}")
            return (False, f"词汇表创建失败: {e!s}")

        ModuleService._init_module_sample_data(module_id)

        module.is_installed = True
        module.installed_at = timezone.now()
        module.save()

        # 注册 cron 任务
        info = ModuleService._load_module_info(module.path) or {}
        for task_path in info.get("cron_tasks", []):
            try:
                from core.services.cron_service import _register_single_task  # noqa: PLC0415

                _register_single_task(task_path)
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
            pass
        except Exception as e:
            logger.warning(f"初始化模块 {module_id} 样本数据失败: {e}")
        return False

    @staticmethod
    def register_and_install(module_info: dict[str, Any]) -> Module:
        module = ModuleService.register_module(module_info)
        if module:
            if not module.is_installed:
                success, msg = ModuleService.install_module(module_info["id"])
                if not success:
                    logger.error(f"模块 {module_info['id']} 安装失败: {msg}")
                    raise RuntimeError(f"模块 {module_info['id']} 安装失败: {msg}")
            if not module.is_active:
                ModuleService.enable_module(module_info["id"])
        return module

    @staticmethod
    def create_module_taxonomies(module: Module) -> int:
        module_info = ModuleService._load_module_info(module.path)
        if not module_info:
            return 0

        taxonomies = module_info.get("taxonomies", [])
        if not taxonomies:
            return 0

        created_count = 0
        slugs = [t.get("slug") for t in taxonomies if t.get("slug") and t.get("name")]
        existing_taxonomies = {t.slug: t for t in Taxonomy.objects.filter(slug__in=slugs)}
        existing_items = {
            (item.taxonomy_id, item.name): item for item in TaxonomyItem.objects.filter(taxonomy__slug__in=slugs)
        }

        items_to_create = []
        new_taxonomies = []

        for tax_data in taxonomies:
            slug = tax_data.get("slug")
            name = tax_data.get("name")
            items = tax_data.get("items", [])

            if not slug or not name:
                continue

            existing = existing_taxonomies.get(slug)
            if existing:
                items_to_create.extend(
                    TaxonomyItem(taxonomy=existing, name=item_name, weight=0)
                    for item_name in items
                    if (existing.id, item_name) not in existing_items
                )
                continue

            taxonomy = Taxonomy(name=name, slug=slug, description=f"{module.name} 模块词汇表")
            new_taxonomies.append(taxonomy)

        Taxonomy.objects.bulk_create(new_taxonomies, ignore_conflicts=True)
        new_slugs = [t.slug for t in new_taxonomies]
        created_taxonomies = {t.slug: t for t in Taxonomy.objects.filter(slug__in=new_slugs)}

        for tax_data in taxonomies:
            slug = tax_data.get("slug")
            items = tax_data.get("items", [])

            if slug in created_taxonomies:
                taxonomy = created_taxonomies[slug]
                for idx, item_name in enumerate(items):
                    items_to_create.append(TaxonomyItem(taxonomy=taxonomy, name=item_name, weight=idx))
                created_count += 1

        if items_to_create:
            TaxonomyItem.objects.bulk_create(items_to_create, ignore_conflicts=True)

        # 验证创建结果
        for tax_data in taxonomies:
            slug = tax_data.get("slug")
            name = tax_data.get("name")
            items = tax_data.get("items", [])

            if not slug or not name:
                continue

            # 验证词汇表是否存在
            taxonomy = Taxonomy.objects.filter(slug=slug).first()
            if not taxonomy:
                raise RuntimeError(f"词汇表创建失败: {slug}")

            # 验证词汇项是否完整
            existing_items = set(taxonomy.items.values_list("name", flat=True))
            expected_items = set(items)
            missing_items = expected_items - existing_items

            if missing_items:
                logger.warning(f"词汇表 {slug} 缺少项目: {missing_items}，尝试补充")
                # 尝试补充缺失的词汇项
                for item_name in missing_items:
                    TaxonomyItem.objects.create(taxonomy=taxonomy, name=item_name, weight=0)

        return created_count

    @staticmethod
    def check_dependencies(module_id: str, visited: set | None = None) -> tuple:
        if visited is None:
            visited = set()

        if module_id in visited:
            chain = " -> ".join([*list(visited), module_id])
            return False, f"发现循环依赖：{chain}", []
        visited.add(module_id)

        module_info = ModuleService._load_module_info(module_id)
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

            ok, err, chain = ModuleService.check_dependencies(dep_id, visited.copy())
            if not ok:
                return False, err, [dep_id, *chain]

        return True, "", []

    @staticmethod
    def verify_dependencies(module_id: str) -> tuple:
        """验证模块依赖，返回(成功?, 错误信息, 依赖链)"""
        ok, err, chain = ModuleService.check_dependencies(module_id)
        return ok, err, chain

    @staticmethod
    def get_dependency_chain(module_id: str) -> list:
        def collect_chain(cid, visited, chain):
            if cid in visited:
                return
            visited.add(cid)

            module_info = ModuleService._load_module_info(cid)
            dep_module = Module.objects.filter(module_id=cid).first()
            if not dep_module:
                logger.warning(f"依赖模块未注册: {cid}")
                return False, f"需要「{module_info.get('name', cid)}」已安装并启用（当前状态：未注册）", []

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

    @staticmethod
    def enable_module(module_id: str) -> Module | None:
        try:
            module = Module.objects.get(module_id=module_id)
        except Module.DoesNotExist:
            logger.warning(f"模块未找到: module_id={module_id}")
            return None

        try:
            if module.is_installed:
                module.is_active = True
                module.activated_at = timezone.now()
                module.save(update_fields=["is_active", "activated_at"])

                # 注册 cron 任务
                info = ModuleService._load_module_info(module.path) or {}
                for task_path in info.get("cron_tasks", []):
                    from core.services.cron_service import _register_single_task  # noqa: PLC0415

                    _register_single_task(task_path)

                if module.module_type == "node":
                    node_type = NodeType.objects.filter(slug=module.module_id).first()
                    if not node_type:
                        logger.warning(f"节点类型未找到: {module.module_id}")
                        return None
                    node_type.is_active = True
                    node_type.save(update_fields=["is_active"])
                elif module.module_type == "tool":
                    tool_type = ToolType.objects.filter(slug=module.module_id).first()
                    if not tool_type:
                        logger.warning(f"工具类型未找到: {module.module_id}")
                        return None
                    tool_type.is_active = True
                    tool_type.save(update_fields=["is_active"])

                return module
        except Module.DoesNotExist:
            pass
        return None

    @staticmethod
    def disable_module(module_id: str) -> Module | None:
        try:
            module = Module.objects.get(module_id=module_id)
        except Module.DoesNotExist:
            logger.warning(f"模块未找到: module_id={module_id}")
            return None

        try:
            module.is_active = False
            module.save(update_fields=["is_active"])

            # 注销 cron 任务
            info = ModuleService._load_module_info(module.path) or {}
            for task_path in info.get("cron_tasks", []):
                from core.services.cron_service import _unregister_single_task  # noqa: PLC0415

                _unregister_single_task(task_path)

            if module.module_type == "node":
                node_type = NodeType.objects.filter(slug=module.module_id).first()
                if not node_type:
                    logger.warning(f"节点类型未找到: {module.module_id}")
                    return None
                node_type.is_active = False
                node_type.save(update_fields=["is_active"])
            elif module.module_type == "tool":
                tool_type = ToolType.objects.filter(slug=module.module_id).first()
                if not tool_type:
                    logger.warning(f"工具类型未找到: {module.module_id}")
                    return None
                tool_type.is_active = False
                tool_type.save(update_fields=["is_active"])

            return module
        except Module.DoesNotExist:
            pass
        return None

    @staticmethod
    def cleanup_uninstalled_modules() -> list[str]:
        registered_modules = Module.objects.filter(is_installed=True)
        cleaned = []

        for module in registered_modules:
            module_path = Path(ModuleService.MODULES_DIR) / module.path
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
        """获取模块，不存在返回None"""
        return Module.objects.filter(module_id=module_id).first()
        # 调用者必须检查返回值是否为None

    @staticmethod
    def sync_node_type(module: Module) -> NodeType:
        module_info = ModuleService._load_module_info(module.path)
        icon = module_info.get("icon", "bi-folder") if module_info else "bi-folder"

        node_type = NodeType.objects.filter(slug=module.module_id).first()

        if not node_type:
            node_type = NodeType.objects.create(
                name=module.name,
                slug=module.module_id,
                description=module.description or "",
                icon=icon,
                is_active=module.is_active,
            )
        else:
            node_type.name = module.name
            node_type.description = module.description or ""
            node_type.icon = icon
            node_type.is_active = module.is_active
            node_type.save()

        return node_type

    @staticmethod
    def sync_tool_type(module: Module) -> ToolType:
        module_info = ModuleService._load_module_info(module.path)
        icon = module_info.get("icon", "bi-wrench") if module_info else "bi-wrench"

        tool_type = ToolType.objects.filter(slug=module.module_id).first()

        if not tool_type:
            tool_type = ToolType.objects.create(
                name=module.name,
                slug=module.module_id,
                description=module.description or "",
                icon=icon,
                is_active=module.is_active,
            )
        else:
            tool_type.name = module.name
            tool_type.description = module.description or ""
            tool_type.icon = icon
            tool_type.is_active = module.is_active
            tool_type.save()

        return tool_type

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
        module_path = Path(ModuleService.MODULES_DIR) / module_id

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
