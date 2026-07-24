"""
QueryService - 查询与筛选处理

提供筛选条件构建、QuerySet 过滤等功能
"""

import json
import logging

from django.db import models
from django.db.models import Q

logger = logging.getLogger(__name__)


class QueryServiceMixin:
    @classmethod
    def _get_filtered_queryset(cls, node_type_slug: str, filters: list[dict] | None = None):
        """获取应用筛选条件后的 QuerySet"""
        from core.importexport.model_registry import ModelRegistry  # noqa: PLC0415  # 惰性：避免循环导入

        model_class = ModelRegistry.get_model(node_type_slug)
        if not model_class:
            from core.node.models import Node  # noqa: PLC0415  # 惰性：node.models 会间接依赖本模块

            queryset = Node.objects.filter(node_type__slug=node_type_slug)
            return cls._apply_filters(queryset, filters, node_type_slug, None, None)

        from django.db.models import ForeignKey  # noqa: PLC0415

        fk_fields = [f.name for f in model_class._meta.get_fields() if isinstance(f, ForeignKey)]
        queryset = model_class.objects.all().select_related(*fk_fields)

        if not filters:
            return queryset

        return cls._apply_filters(queryset, filters, node_type_slug, model_class, None)

    @classmethod
    def build_filter_summaries(cls, node_type_slug: str, filters: list) -> list:
        """构建过滤器摘要，用于导出预览页面的筛选条件展示"""
        if not filters:
            return []

        all_fields = cls.get_exportable_fields(node_type_slug)
        field_map = {f["name"]: f["label"] for f in all_fields}

        summaries = []
        for f in filters:
            field = f.get("field", "")
            value = f.get("value", "")

            if field == "region":
                try:
                    region_data = json.loads(value) if isinstance(value, str) else value
                except (json.JSONDecodeError, TypeError):
                    region_data = {}
                parts = [
                    v
                    for v in [
                        region_data.get("province", ""),
                        region_data.get("city", ""),
                        region_data.get("district", ""),
                    ]
                    if v
                ]
                if parts:
                    summaries.append({"label": "省市区", "value": " ".join(parts)})
            else:
                label = field_map.get(field, field)
                summaries.append({"label": label, "value": value})

        return summaries

    @classmethod
    def _apply_filters(
        cls,
        queryset,
        filters: list[dict],
        node_type_slug: str,
        model_class: type | None = None,
        model_related_name: str | None = None,
    ):
        """应用筛选条件"""

        is_direct_query = model_class is not None and model_related_name is None

        for f in filters:
            field = f.get("field", "")
            value = f.get("value", "")

            if not field or not value:
                continue

            if field == "region":
                try:
                    region_data = json.loads(value) if isinstance(value, str) else value
                except (json.JSONDecodeError, TypeError):
                    region_data = {}
                q = Q()
                province = region_data.get("province", "")
                city = region_data.get("city", "")
                district = region_data.get("district", "")

                prefix = model_related_name or ("" if is_direct_query else f"{node_type_slug}_fields")
                if province:
                    q &= Q(
                        **{f"{prefix}__region__province__icontains": province}
                        if prefix
                        else Q(region__province__icontains=province)
                    )
                if city:
                    q &= Q(
                        **{f"{prefix}__region__city__icontains": city} if prefix else Q(region__city__icontains=city)
                    )
                if district:
                    q &= Q(
                        **{f"{prefix}__region__district__icontains": district}
                        if prefix
                        else Q(region__district__icontains=district)
                    )

                queryset = queryset.filter(q)
            elif model_class and hasattr(model_class, field):
                field_obj = model_class._meta.get_field(field)
                if isinstance(field_obj, models.ForeignKey):
                    lookup = f"{field}__name__icontains"
                    queryset = queryset.filter(**{lookup: value})
                elif isinstance(
                    field_obj,
                    (models.CharField, models.TextField, models.EmailField, models.URLField, models.SlugField),
                ):
                    queryset = queryset.filter(**{f"{field}__icontains": value})
                else:
                    queryset = queryset.filter(**{f"{field}__exact": value})

        return queryset
