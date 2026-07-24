"""
TransformerService - 数据转换服务

提供行数据转换、外键解析、特殊字段处理等功能
"""

from core.importexport.fk_resolver import FKResolverPool
from core.importexport.special_field_handler import SpecialFieldPool

from .validator_service import convert_boolean


def transform_row(row: dict, node_type_slug: str, field_map: dict, fk_overrides: dict) -> dict:
    """转换行数据"""
    transformed = {}

    for field_name, value in row.items():
        if field_name not in field_map:
            continue

        field = field_map[field_name]
        field_type = field["type"]

        if value is None or (isinstance(value, str) and not value.strip()):
            continue

        if field_type == "fk":
            fk_to = field.get("fk_to")
            if fk_to:
                taxonomy_slug = fk_overrides.get(
                    (node_type_slug, field_name), field.get("taxonomy", field_name)
                )
                resolved = FKResolverPool.resolve(fk_to, value, taxonomy_slug, auto_create=True)
                if resolved is not None:
                    transformed[field_name] = resolved

        elif field_type == "json":
            if SpecialFieldPool.is_special_field(field_name):
                transformed[field_name] = SpecialFieldPool.handle_import(field_name, value)
            else:
                transformed[field_name] = value

        elif field_type == "boolean":
            transformed[field_name] = convert_boolean(value)

        else:
            transformed[field_name] = value

    return transformed
