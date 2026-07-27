import logging
import shutil
from pathlib import Path
from typing import Any

from core.module.models import Module, ToolType
from core.node.models import NodeType

logger = logging.getLogger(__name__)


class ModuleScaffoldService:
    MODULES_DIR = "modules"

    @classmethod
    def _sync_type(cls, module: Module, model_class, default_icon: str):
        from core.module.services.module_scan_service import ModuleScanService  # noqa: PLC0415

        module_info = ModuleScanService.load_module_info(module.path)
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
            type_obj.save(update_fields=["name", "description", "icon", "is_active"])

        return type_obj

    @classmethod
    def sync_node_type(cls, module: Module) -> NodeType:
        return cls._sync_type(module, NodeType, "bi-folder")

    @classmethod
    def sync_tool_type(cls, module: Module):
        return cls._sync_type(module, ToolType, "bi-wrench")

    @classmethod
    def create_module(
        cls,
        module_id: str,
        name: str,
        module_type: str = "node",
        description: str = "",
        icon: str = "bi-folder",
        install_on_init: bool = True,
        author: str = "",
    ) -> dict[str, Any]:
        module_path = Path(cls.MODULES_DIR) / module_id

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
from core.decorators import login_required_json


@login_required_json
@require_http_methods(["GET"])
def list_view(request):
    return JsonResponse({{'message': 'List view for {module_id}'}})


@login_required_json
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

            snapshot_content = f"""# {module_id} 模块快照

## 模型
| 模型 | 字段 |
|------|------|

## 服务类
| 方法 | 参数 |
|------|------|

## 文件
- `modules/{module_id}/models.py` (0 行)
- `modules/{module_id}/views.py` (0 行)
- `modules/{module_id}/module.py` (0 行)
"""
            with (module_path / "SNAPSHOT.md").open("w") as f:
                f.write(snapshot_content)

            return {"success": True, "module_id": module_id, "path": module_path}

        except PermissionError:
            return {"success": False, "error": "权限不足，无法创建目录"}
        except Exception as e:
            logger.exception("创建模块 %s 失败", module_id)
            if module_path.exists():
                shutil.rmtree(module_path)
            return {"success": False, "error": f"创建模块失败: {e!s}"}
