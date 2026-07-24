"""
ValueResolver - 字段值解析

提供字段值获取、FK 字段解析、省市区字段解析等功能
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ValueResolverMixin:
    @classmethod
    def _convert_to_row(
        cls, item, field_names: list[str], field_type_map: dict[str, str], _node_type_slug: str | None = None
    ) -> dict:
        """将数据对象转换为导出行"""
        row = {}

        for field_name in field_names:
            field_type = field_type_map.get(field_name, "string")
            value = cls._get_field_value(item, field_name, field_type)
            row[field_name] = value

        return row

    @classmethod
    def _get_field_value(cls, obj: Any, field_name: str, field_type: str = "string") -> Any:
        """获取字段值"""
        if obj is None:
            return ""

        if field_type in ["fk", "taxonomy"]:
            return cls._resolve_fk_field(obj, field_name)

        if field_type == "region":
            return cls._resolve_region_field(obj)

        if field_type == "boolean":
            value = getattr(obj, field_name, False)
            return "是" if value else "否"

        if field_type == "datetime":
            value = getattr(obj, field_name, None)
            if value:
                return value.strftime("%Y-%m-%d %H:%M:%S")
            return ""

        if field_type == "date":
            value = getattr(obj, field_name, None)
            if value:
                return value.strftime("%Y-%m-%d")
            return ""

        return getattr(obj, field_name, "") or ""

    @classmethod
    def _resolve_fk_field(cls, obj: Any, field_name: str) -> str:
        """解析 FK 字段，返回名称"""
        fk_obj = getattr(obj, field_name, None)
        if fk_obj is None:
            return ""

        if hasattr(fk_obj, "name"):
            return fk_obj.name
        return str(fk_obj)

    @classmethod
    def _resolve_region_field(cls, obj: Any) -> str:
        """解析省市区 JSON 字段"""
        region = getattr(obj, "region", None) or {}
        if isinstance(region, str):
            try:
                region = json.loads(region)
            except (json.JSONDecodeError, TypeError):
                return region

        province = region.get("province", "")
        city = region.get("city", "")
        district = region.get("district", "")
        parts = [p for p in [province, city, district] if p]
        return " ".join(parts) if parts else ""
