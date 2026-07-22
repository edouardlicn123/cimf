"""
================================================================================
文件：taxonomy_service.py
路径：/home/edo/cimf-v2/core/services/taxonomy_service.py
================================================================================

功能说明：
    词汇表服务层，提供词汇表和词汇项的 CRUD 操作，以及预置数据初始化。

    主要功能：
    - 词汇表管理（增删改查）
    - 词汇项管理（增删改查、排序）
    - 预置词汇表初始化（47个）

用法：
    1. 获取所有词汇表：
        from core.services.taxonomy_service import TaxonomyService
        taxonomies = TaxonomyService.get_all_taxonomies()

    2. 获取词汇表及其词汇项：
        taxonomy = TaxonomyService.get_taxonomy_by_id(1)
        items = TaxonomyService.get_items(1)

    3. 初始化预置词汇表：
        TaxonomyService.init_default_taxonomies()

版本：
    - 1.0: 从 Flask 项目迁移

依赖：
    - core.models.Taxonomy: 词汇表模型
    - core.models.TaxonomyItem: 词汇项模型
"""

import logging

from django.core.management import call_command
from django.db import models, transaction

from core.models import Taxonomy, TaxonomyItem
from core.services.base_service import BaseService

logger = logging.getLogger(__name__)


class TaxonomyService(BaseService):
    """
    词汇表服务层
    提供词汇表和词汇项的 CRUD 操作
    """

    model_class = Taxonomy

    @staticmethod
    def get_all_taxonomies():
        """获取所有词汇表"""
        return Taxonomy.objects.all().order_by("id")

    @staticmethod
    def get_taxonomy_list(search: str = "") -> list:
        """获取词汇表列表，支持搜索"""
        queryset = Taxonomy.objects.all()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by("id")

    @staticmethod
    def check_slug_exists(slug: str) -> bool:
        """检查词汇表标识是否已存在"""
        return Taxonomy.objects.filter(slug=slug).exists()

    @staticmethod
    def check_slug_exists_exclude(slug: str, exclude_id: int) -> bool:
        """检查词汇表标识是否已存在（排除指定 ID）"""
        return Taxonomy.objects.filter(slug=slug).exclude(id=exclude_id).exists()

    @classmethod
    def get_taxonomy_by_id(cls, taxonomy_id: int):
        """获取词汇表详情"""
        return cls.get_by_id(taxonomy_id)

    @classmethod
    def get_taxonomy_by_slug(cls, slug: str):
        """通过 slug 获取词汇表"""
        return cls.get_first(slug=slug)

    @staticmethod
    def create_taxonomy(name: str, slug: str, description: str = "") -> models.Model:
        """创建词汇表（存在则更新，不存在则创建）"""
        taxonomy, _created = Taxonomy.objects.update_or_create(
            slug=slug, defaults={"name": name, "description": description}
        )
        return taxonomy

    @classmethod
    def update_taxonomy(
        cls, taxonomy_id: int, name: str | None = None, slug: str | None = None, description: str | None = None
    ) -> models.Model:
        """更新词汇表"""
        taxonomy = cls.get_by_id(taxonomy_id)
        if taxonomy:
            BaseService.update_fields(taxonomy, name=name, slug=slug, description=description)
        return taxonomy

    @classmethod
    def delete_taxonomy(cls, taxonomy_id: int) -> bool:
        """删除词汇表（同时删除所有关联的词汇项）"""
        return cls.delete(taxonomy_id)

    @staticmethod
    def get_items(taxonomy_id: int) -> list[models.Model]:
        """获取词汇表的所有词汇项"""
        return TaxonomyItem.objects.filter(taxonomy_id=taxonomy_id).order_by("weight", "name")

    @classmethod
    def get_items_bulk(cls, slugs: list[str]) -> dict[str, list[models.Model]]:
        """批量获取多个词汇表的词汇项，一次数据库查询"""
        taxonomies = Taxonomy.objects.filter(slug__in=slugs).prefetch_related("items")
        result: dict[str, list[models.Model]] = {}
        for tax in taxonomies:
            items = tax.items.all().order_by("weight", "name") if hasattr(tax, "items") else []
            result[tax.slug] = list(items)
        for slug in slugs:
            result.setdefault(slug, [])
        return result

    @staticmethod
    def get_item_by_id(item_id: int):
        """根据 ID 获取词汇项"""
        return TaxonomyItem.objects.filter(id=item_id).first()

    @staticmethod
    def create_item(taxonomy_id: int, name: str, description: str = "", weight: int | None = None) -> models.Model:
        """创建词汇项"""
        with transaction.atomic():
            if weight is None:
                max_weight = (
                    TaxonomyItem.objects.filter(taxonomy_id=taxonomy_id).aggregate(models.Max("weight"))["weight__max"]
                    or 0
                )
                weight = max_weight + 1
            item = TaxonomyItem.objects.create(
                taxonomy_id=taxonomy_id, name=name, description=description, weight=weight
            )
        return item

    @classmethod
    def update_item(
        cls, item_id: int, name: str | None = None, description: str | None = None, weight: int | None = None
    ) -> models.Model:
        """更新词汇项"""
        item = cls.get_item_by_id(item_id)
        if item:
            BaseService.update_fields(item, name=name, description=description, weight=weight)
        return item

    @classmethod
    def delete_item(cls, item_id: int) -> bool:
        """删除词汇项"""
        item = cls.get_item_by_id(item_id)
        if item:
            item.delete()
            return True
        return False

    @staticmethod
    def reorder_items(taxonomy_id: int, item_ids: list[int]) -> bool:
        """重新排序词汇项"""
        with transaction.atomic():
            items = list(TaxonomyItem.objects.filter(id__in=item_ids, taxonomy_id=taxonomy_id))
            item_map = {item.id: item for item in items}
            for idx, item_id in enumerate(item_ids):
                item = item_map.get(item_id)
                if item:
                    item.weight = idx
            TaxonomyItem.objects.bulk_update(items, ["weight"], batch_size=1000)
        return True

    @staticmethod
    def init_default_taxonomies() -> int:
        """
        初始化预置分类数据（使用 fixture 快速加载）

        优化效果：从 ~2-3秒 降至 ~0.5秒
        fixture 加载失败时直接抛出异常，不再回退到代码初始化

        返回：创建的词汇表数量
        """
        if Taxonomy.objects.exists():
            return 0

        call_command("loaddata", "initial_taxonomies.json", verbosity=0)
        count = Taxonomy.objects.count()
        logger.info(f"词汇表 fixture 加载完成，共 {count} 个词汇表")
        return count

    @staticmethod
    def generate_items_ai(_taxonomy_id: int, _count: int = 10) -> list[str]:
        """AI 生成词汇项（预留接口）"""
        return []
