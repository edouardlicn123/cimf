import ast
import logging
from pathlib import Path
from typing import Any

from core.module.models import Module

logger = logging.getLogger(__name__)


class ModuleScanService:
    MODULES_DIR = "modules"
    _module_info_cache: dict[str, dict[str, Any]] = {}

    @classmethod
    def _parse_node(cls, node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.NameConstant):
            return node.value
        elif isinstance(node, ast.List):
            return [cls._parse_node(elem) for elem in node.elts]
        elif isinstance(node, ast.Dict):
            result = {}
            for k, v in zip(node.keys, node.values, strict=False):
                key = cls._parse_node(k)
                value = cls._parse_node(v)
                if key is not None:
                    result[key] = value
            return result
        else:
            return None

    @classmethod
    def load_module_info(cls, module_dir: str) -> dict[str, Any] | None:
        if module_dir in cls._module_info_cache:
            return cls._module_info_cache[module_dir]

        try:
            module_file = Path(cls.MODULES_DIR) / module_dir / "module.py"

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
                            module_info = cls._parse_node(node.value)

                            if not isinstance(module_info, dict):
                                return None

                            if "id" not in module_info:
                                raise ValueError(f"模块 {module_dir} 缺少 id 字段")
                            if "type" not in module_info:
                                raise ValueError(f"模块 {module_dir} 缺少 type 字段")

                            cls._module_info_cache[module_dir] = module_info
                            return module_info

            return None

        except ValueError:
            raise
        except Exception as e:
            logger.warning(f"解析模块 {module_dir} 信息失败: {e}")
            return None

    @classmethod
    def register_module(cls, module_info: dict[str, Any]) -> Module:
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
                existing.save(update_fields=["name", "version", "description", "icon"])
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

    @classmethod
    def scan_modules(cls) -> list[dict[str, Any]]:
        modules = []
        base_path = cls.MODULES_DIR

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
            module_info = cls.load_module_info(item)
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

    @classmethod
    def scan_register_install(
        cls, do_install: bool = True, dry_run: bool = False, respect_install_on_init: bool = True
    ) -> dict[str, Any]:
        all_modules = cls.scan_modules()

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

        pending_ids = [m["id"] for m in pending if m.get("is_registered")]
        registered_modules = (
            {m.module_id: m for m in Module.objects.filter(module_id__in=pending_ids)} if pending_ids else {}
        )

        skipped_due_to_install_on_init = 0
        if respect_install_on_init:
            filtered_pending = []
            for m in pending:
                if m.get("is_registered"):
                    module_obj = registered_modules.get(m["id"])
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

        from core.module.services.module_install_service import ModuleInstallService  # noqa: PLC0415

        for m in pending:
            try:
                module = cls.register_module(m)
                result["registered"] += 1

                if do_install and not module.is_installed:
                    ok, msg = ModuleInstallService.install_module(m["id"])
                    if ok:
                        result["installed"] += 1
                    else:
                        result["failed"].append(f"{m.get('name', m['id'])}: {msg}")
            except Exception as e:
                logger.warning("模块注册安装失败: %s — %s", m["id"], e, exc_info=True)
                result["failed"].append(f"{m.get('name', m['id'])}: {e!s}")

        return result

    @classmethod
    def scan_and_register_modules(cls) -> list[Module]:
        cls.scan_register_install(do_install=True, dry_run=False)

        registered = Module.objects.filter(is_installed=True)
        return list(registered)

    @classmethod
    def auto_register_missing(cls) -> dict[str, Any]:
        """扫描 modules/ 目录，自动注册尚未注册的模块"""
        from django.db import connection  # noqa: PLC0415

        try:
            table_names = connection.introspection.table_names()
            if "modules" not in table_names:
                logger.debug("modules 表不存在，跳过自动注册")
                return {"registered": 0, "message": "数据库未就绪"}
        except Exception:
            logger.warning("数据库未就绪，跳过自动注册", exc_info=True)
            return {"registered": 0, "message": "数据库未就绪"}

        return cls.scan_register_install(do_install=True, dry_run=False, respect_install_on_init=True)
