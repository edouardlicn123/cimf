"""
FieldService - 字段发现与配置管理

提供可导出字段的自动发现、模块配置管理等
"""

import logging

from core.module.services.module_registry_service import ModuleRegistryService

logger = logging.getLogger(__name__)


class FieldServiceMixin:
    """可导出的字段类型"""
    EXPORTABLE_FIELD_TYPES = [
        "string",
        "string_long",
        "text",
        "email",
        "telephone",
        "integer",
        "decimal",
        "float",
        "boolean",
        "entity_reference",
        "datetime",
        "date",
    ]

    FK_TYPES = ["fk", "taxonomy", "region"]

    FILTERABLE_TYPES = ["string", "string_long", "text", "email", "telephone", "fk"]

    FILTERABLE_FK_FIELDS = ["country", "industry", "enterprise_nature", "enterprise_type"]

    @classmethod
    def get_exportable_fields(cls, node_type_slug: str) -> list[dict]:
        """
        动态获取可导出的字段列表

        优先级：
        1. 模块配置的 export_fields（支持覆盖/补充/排除）
        2. 自动从 Django 模型发现
        """
        from core.importexport.field_extractor import FieldDefExtractor  # noqa: PLC0415
        from core.importexport.model_registry import ModelRegistry  # noqa: PLC0415

        module_config = cls._get_module_export_config(node_type_slug)

        if module_config is not None:
            auto_fields = cls._auto_discover_fields(node_type_slug, ModelRegistry, FieldDefExtractor)
            return FieldDefExtractor.merge_with_module_config(auto_fields, module_config)

        return cls._auto_discover_fields(node_type_slug, ModelRegistry, FieldDefExtractor)

    @classmethod
    def _auto_discover_fields(cls, node_type_slug: str, model_registry, field_def_extractor) -> list[dict]:
        """自动从 Django 模型发现字段"""
        model_class = model_registry.get_model(node_type_slug)
        if model_class:
            return field_def_extractor.extract(model_class)
        return []

    @classmethod
    def _get_module_export_config(cls, node_type_slug: str) -> list[dict] | None:
        """获取模块配置的导出字段定义"""
        try:
            mod = ModuleRegistryService.import_module_sub(node_type_slug, "module")
            if hasattr(mod, "MODULE_INFO"):
                config = mod.MODULE_INFO.get("export_fields")
                if config:
                    return config
        except (ImportError, ModuleNotFoundError):
            pass
        return None

    @classmethod
    def get_fields_info(cls, node_type_slug: str, field_names: list[str]) -> list[dict]:
        """获取选中字段的详细信息"""
        all_fields = cls.get_exportable_fields(node_type_slug)
        return [f for f in all_fields if f["name"] in field_names]

    @classmethod
    def get_filterable_fields(cls, node_type_slug: str) -> list[dict]:
        """获取可筛选的字段列表"""
        all_fields = cls.get_exportable_fields(node_type_slug)
        return [f for f in all_fields if f["type"] in cls.FILTERABLE_TYPES]

    @classmethod
    def has_region_field(cls, node_type_slug: str) -> bool:
        """检查节点类型是否有省市区 JSON 字段"""
        all_fields = cls.get_exportable_fields(node_type_slug)
        return any(f["name"] == "region" for f in all_fields)
