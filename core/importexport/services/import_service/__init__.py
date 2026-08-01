"""
ImportService - 导入服务

提供通用的数据导入功能，支持 CSV/Excel 格式
"""

import logging
import threading
from typing import Any

from django.db import transaction
from django.http import HttpResponse

from core.module.services.module_registry_service import ModuleRegistryService

from . import reader_service, transformer_service, validator_service

logger = logging.getLogger(__name__)


class ImportService:
    """通用导入服务"""

    FORMAT_CSV = reader_service.FORMAT_CSV
    FORMAT_XLSX = reader_service.FORMAT_XLSX
    MAX_FILE_SIZE = reader_service.MAX_FILE_SIZE

    _import_lock = threading.Lock()

    FK_TAXONOMY_OVERRIDES = {
        ("customer_cn", "enterprise_type"): "enterprise_nature",
    }

    @classmethod
    def get_importable_fields(cls, node_type_slug: str) -> list[dict]:
        """获取可导入的字段列表"""
        from core.importexport.field_extractor import FieldDefExtractor  # noqa: PLC0415
        from core.importexport.model_registry import ModelRegistry  # noqa: PLC0415

        model_class = ModelRegistry.get_model(node_type_slug)
        if not model_class:
            return []

        return FieldDefExtractor.extract(model_class)

    @classmethod
    def read_file(cls, file, format: str) -> tuple[list[str], list[list[str]]]:
        """读取文件内容，含大小检查"""
        return reader_service.read_file(file, format)

    @classmethod
    def map_headers_to_fields(cls, headers: list[str], fields: list[dict]) -> dict[str, str]:
        """将文件头部映射到字段定义"""
        header_to_field = {}
        header_lower_map = {h.lower(): h for h in headers}

        for field in fields:
            field_label = field["label"].lower()

            if field_label in header_lower_map:
                header_to_field[header_lower_map[field_label]] = field["name"]
            else:
                field_name = field["name"].lower()
                if field_name in header_lower_map:
                    header_to_field[header_lower_map[field_name]] = field["name"]

        return header_to_field

    @classmethod
    def parse_data(cls, headers: list[str], data_rows: list[list[str]], header_to_field: dict[str, str]) -> list[dict]:
        """解析数据行"""
        parsed_rows = []

        for row in data_rows:
            row_dict = {}
            for i, cell in enumerate(row):
                if i < len(headers):
                    header = headers[i]
                    if header in header_to_field:
                        field_name = header_to_field[header]
                        row_dict[field_name] = str(cell).strip() if cell else ""

            parsed_rows.append(row_dict)

        return parsed_rows

    @classmethod
    def validate_data(cls, node_type_slug: str, rows: list[dict]) -> dict:
        """验证数据"""
        fields = cls.get_importable_fields(node_type_slug)
        field_map = {f["name"]: f for f in fields}

        valid_count = 0
        errors = []

        for idx, row in enumerate(rows, start=1):
            row_errors = []

            for field_name, value in row.items():
                if field_name not in field_map:
                    continue

                field = field_map[field_name]
                field_errors = cls._validate_field(field, value)
                row_errors.extend(field_errors)

            if row_errors:
                errors.append(
                    {
                        "row": idx,
                        "data": row,
                        "errors": row_errors,
                    }
                )
            else:
                valid_count += 1

        return {
            "valid_count": valid_count,
            "error_count": len(errors),
            "errors": errors,
        }

    @classmethod
    def _validate_field(cls, field: dict, value: Any) -> list[str]:
        """验证单个字段

        注意：对于外键(FK)字段，只验证数据类型是否有效，不验证值是否在词汇表中存在。
        外键值的映射和自动创建在数据转换阶段处理。
        """
        errors = []

        if not value:
            if field["required"]:
                errors.append(f"{field['label']} 不能为空")
            return errors

        field_type = field["type"]

        if field_type == "email":
            if not validator_service.is_valid_email(value):
                errors.append(f"{field['label']} 邮箱格式不正确")

        elif field_type == "json":
            from core.importexport.special_field_handler import SpecialFieldPool  # noqa: PLC0415

            if SpecialFieldPool.is_special_field(field["name"]):
                pass

        return errors

    @classmethod
    def _is_valid_email(cls, email: str) -> bool:
        """验证邮箱格式"""
        return validator_service.is_valid_email(email)

    @staticmethod
    def _convert_boolean(value: Any) -> bool:
        """将多种布尔表示转换为 Python Boolean"""
        return validator_service.convert_boolean(value)

    @classmethod
    def _get_import_row(cls, slug: str):
        """尝试获取模块的 import_row 方法"""
        try:
            mod = ModuleRegistryService.import_module_sub(slug, "services")
            for attr_name in dir(mod):
                obj = getattr(mod, attr_name)
                if isinstance(obj, type) and hasattr(obj, "import_row"):
                    return obj.import_row
        except (ImportError, ModuleNotFoundError):
            pass
        return None

    @classmethod
    def import_data(cls, node_type_slug: str, rows: list[dict], user, skip_duplicates: bool = True) -> dict:
        """执行导入（线程安全，同一时间只允许一个导入任务）"""
        if not cls._import_lock.acquire(blocking=False):
            return {
                "success_count": 0,
                "warning_count": 0,
                "warning_details": [],
                "error_count": 1,
                "errors": [{"row": 0, "data": {}, "errors": ["导入服务忙，请稍后再试"]}],
            }
        try:
            return cls._do_import(node_type_slug, rows, user, skip_duplicates)
        finally:
            cls._import_lock.release()

    @classmethod
    def _do_import(cls, node_type_slug: str, rows: list[dict], user, skip_duplicates: bool = True) -> dict:
        """执行导入（内部方法，由 import_data 加锁调用）"""
        from core.importexport.model_registry import ModelRegistry  # noqa: PLC0415
        from core.node.models import Node, NodeType  # noqa: PLC0415

        model_class = ModelRegistry.get_model(node_type_slug)
        fields = cls.get_importable_fields(node_type_slug)
        field_map = {f["name"]: f for f in fields}

        success_count = 0
        errors = []
        warnings = []

        node_type = NodeType.objects.filter(slug=node_type_slug).first()
        if not node_type:
            raise ValueError(f"未找到节点类型: {node_type_slug}")

        import_row = cls._get_import_row(node_type_slug)

        for idx, row in enumerate(rows, start=1):
            try:
                with transaction.atomic():
                    transformed = transformer_service.transform_row(row, node_type_slug, field_map, cls.FK_TAXONOMY_OVERRIDES)

                    existing = cls._find_existing(model_class, transformed)

                    if existing:
                        if skip_duplicates:
                            warnings.append(
                                {
                                    "row": idx,
                                    "data": row,
                                    "message": "记录已存在，已跳过",
                                }
                            )
                            continue
                        instance = existing
                    elif import_row:
                        instance = import_row(transformed, user)
                    else:
                        node = Node.objects.create(
                            node_type=node_type,
                            created_by=user,
                            updated_by=user,
                        )
                        instance = model_class.objects.create(node=node)
                        modified = []
                        for key, value in transformed.items():
                            setattr(instance, key, value)
                            modified.append(key)
                        instance.save(update_fields=modified)
                success_count += 1

            except Exception as e:
                logger.warning(f"导入第 {idx} 行失败: {e}")
                errors.append(
                    {
                        "row": idx,
                        "data": row,
                        "errors": [str(e)],
                    }
                )

        return {
            "success_count": success_count,
            "warning_count": len(warnings),
            "warning_details": warnings,
            "error_count": len(errors),
            "errors": errors,
        }

    @classmethod
    def _find_existing(cls, model_class, data: dict):
        """查找已存在的记录"""
        for field_name, value in data.items():
            try:
                field = model_class._meta.get_field(field_name)
            except Exception:  # noqa: S112, CIMF_W007 — field discovery skip unknown
                continue
            if getattr(field, "unique", False) and value:
                existing = model_class.objects.filter(**{field_name: value}).first()
                if existing:
                    return existing
        return None

    @classmethod
    def get_fk_fields_with_options(cls, node_type_slug: str) -> list[dict]:
        """获取 FK 字段及其可选值"""
        from core.models import Taxonomy, TaxonomyItem  # noqa: PLC0415

        fields = cls.get_importable_fields(node_type_slug)

        result = []

        for field in fields:
            if field["type"] != "fk":
                continue

            field_name = field["name"]

            taxonomy_slug = cls.FK_TAXONOMY_OVERRIDES.get(
                (node_type_slug, field_name), field.get("taxonomy", field_name)
            )

            taxonomy = Taxonomy.objects.filter(slug=taxonomy_slug).first()

            if taxonomy:
                items = list(
                    TaxonomyItem.objects.filter(taxonomy=taxonomy)
                    .values_list("name", flat=True)
                    .order_by("weight", "name")
                )

                result.append({"name": field_name, "label": field["label"], "items": items, "total": len(items)})

        return result

    @classmethod
    def generate_error_csv(cls, errors: list[dict], _fields: list[dict]) -> HttpResponse:
        """生成错误列表 CSV"""
        from core.utils.response import csv_response  # noqa: PLC0415

        headers = ["行号", "错误原因", "数据"]
        data_rows = [
            [
                e.get("row", ""),
                "; ".join(e.get("errors", [])),
                str(e.get("data", "")),
            ]
            for e in errors
        ]

        return csv_response(headers, data_rows, "import_errors.csv", sanitize=True)
