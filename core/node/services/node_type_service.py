import logging
from importlib import import_module
from pathlib import Path
from typing import Any

from core.node.models import Node, NodeType

logger = logging.getLogger(__name__)


class NodeTypeService:
    @staticmethod
    def get_all() -> list[NodeType]:
        return NodeType.objects.filter(is_active=True)

    @staticmethod
    def get_all_including_inactive() -> list[NodeType]:
        return NodeType.objects.all()

    @staticmethod
    def get_by_id(node_type_id: int) -> NodeType | None:
        return NodeType.objects.filter(id=node_type_id).first()  # 调用者需检查 None

    @staticmethod
    def get_by_id_or_404(node_type_id: int) -> NodeType:
        """获取节点类型，不存在则抛出异常"""
        node_type = NodeType.objects.filter(id=node_type_id).first()
        if not node_type:
            raise ValueError(f"节点类型不存在: {node_type_id}")
        return node_type

    @staticmethod
    def get_by_slug(slug: str) -> NodeType | None:
        return NodeType.objects.filter(slug=slug, is_active=True).first()  # 调用者需检查 None

    @staticmethod
    def get_by_slug_or_404(slug: str) -> NodeType:
        """获取节点类型，不存在则抛出异常"""
        node_type = NodeType.objects.filter(slug=slug, is_active=True).first()
        if not node_type:
            raise ValueError(f"节点类型不存在: {slug}")
        return node_type

    @staticmethod
    def get_by_slug_including_inactive(slug: str) -> NodeType | None:
        return NodeType.objects.filter(slug=slug).first()  # 调用者需检查 None

    @staticmethod
    def get_by_slug_including_inactive_or_404(slug: str) -> NodeType:
        """获取节点类型（含未激活），不存在则抛出异常"""
        node_type = NodeType.objects.filter(slug=slug).first()
        if not node_type:
            raise ValueError(f"节点类型不存在: {slug}")
        return node_type

    @staticmethod
    def create(data: dict[str, Any]) -> NodeType:
        return NodeType.objects.create(**data)

    @staticmethod
    def update(node_type_id: int, data: dict[str, Any]) -> NodeType | None:
        node_type = NodeTypeService.get_by_id(node_type_id)
        if node_type:
            changed = []
            for key, value in data.items():
                if hasattr(node_type, key):
                    setattr(node_type, key, value)
                    changed.append(key)
            if changed:
                node_type.save(update_fields=changed)
        return node_type

    @staticmethod
    def delete(node_type_id: int) -> bool:
        node_type = NodeTypeService.get_by_id(node_type_id)
        if node_type:
            node_type.is_active = False
            node_type.save(update_fields=["is_active"])
            return True
        return False

    @staticmethod
    def enable(node_type_id: int) -> bool:
        node_type = NodeTypeService.get_by_id(node_type_id)
        if node_type:
            node_type.is_active = True
            node_type.save(update_fields=["is_active"])
            return True
        return False

    @staticmethod
    def disable(node_type_id: int) -> bool:
        node_type = NodeTypeService.get_by_id(node_type_id)
        if node_type:
            node_type.is_active = False
            node_type.save(update_fields=["is_active"])
            return True
        return False

    @staticmethod
    def toggle_active(node_type_id: int) -> bool:
        node_type = NodeTypeService.get_by_id(node_type_id)
        if node_type:
            node_type.is_active = not node_type.is_active
            node_type.save(update_fields=["is_active"])
            return node_type.is_active
        return False

    @staticmethod
    def get_node_count(node_type_id: int) -> int:
        return Node.objects.filter(node_type_id=node_type_id).count()

    @staticmethod
    def get_node_types_from_modules() -> list[dict[str, Any]]:
        node_types = []
        modules_dir = "modules"

        if not Path(modules_dir).exists():
            return node_types

        for item_path in Path(modules_dir).iterdir():
            if not item_path.is_dir():
                continue

            module_file = item_path / "module.py"
            if not module_file.exists():
                continue

            try:
                mod = import_module(f"modules.{item_path.name}.module")
                if hasattr(mod, "MODULE_INFO"):
                    module_info = mod.MODULE_INFO
                    if module_info.get("type") == "node":
                        node_type_config = module_info.get("node_type", {})
                        if not node_type_config:
                            node_type_config = {
                                "name": module_info.get("name", item_path.name),
                                "slug": module_info.get("id", item_path.name),
                                "description": module_info.get("description", ""),
                                "icon": module_info.get("icon", "bi-folder"),
                            }
                        node_types.append(node_type_config)
            except (ImportError, ModuleNotFoundError, AttributeError):
                logger.warning(f"无法加载模块配置: {item_path.name}/module.py")
                continue

        return node_types

    @staticmethod
    def init_default_node_types() -> None:
        node_types_config = NodeTypeService.get_node_types_from_modules()
        existing_slugs = set(
            NodeType.objects.filter(slug__in=[nt["slug"] for nt in node_types_config if nt.get("slug")]).values_list(
                "slug", flat=True
            )
        )
        for nt_data in node_types_config:
            slug = nt_data.get("slug")
            if not slug or slug in existing_slugs:
                continue

            NodeType.objects.create(
                name=nt_data.get("name", slug),
                slug=slug,
                description=nt_data.get("description", ""),
                icon=nt_data.get("icon", "bi-folder"),
                fields_config=nt_data.get("fields_config", []),
                is_active=nt_data.get("is_active", True),
            )
