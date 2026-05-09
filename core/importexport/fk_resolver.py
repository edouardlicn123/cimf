# -*- coding: utf-8 -*-
"""
外键解析器

解析外键字段的值，查找对应的 TaxonomyItem 等
"""

from typing import Optional, Any


class FKResolverPool:
    """外键解析器池"""
    
    _resolvers = {}
    
    @classmethod
    def register(cls, model_name: str, resolver):
        """注册解析器"""
        cls._resolvers[model_name] = resolver
    
    @classmethod
    def resolve(cls, fk_model_or_name, value: str, taxonomy_slug: Optional[str] = None, auto_create: bool = True) -> Any:
        """解析外键值"""
        if not value:
            return None

        if isinstance(fk_model_or_name, str):
            model_name = fk_model_or_name
        else:
            model_name = fk_model_or_name._meta.model_name

        if model_name in cls._resolvers:
            return cls._resolvers[model_name].resolve(value, taxonomy_slug)

        return cls._default_resolve(fk_model_or_name, value, taxonomy_slug, auto_create)
    
    @staticmethod
    def _default_resolve(fk_model_or_name, value: str, taxonomy_slug: Optional[str] = None, auto_create: bool = True) -> Any:
        """默认解析逻辑，支持自动创建词汇表项"""
        from core.models import TaxonomyItem, Taxonomy

        if not value:
            return None

        if isinstance(fk_model_or_name, str):
            model_name = fk_model_or_name
        else:
            model_name = fk_model_or_name._meta.model_name

        if model_name == 'taxonomyitem':
            if taxonomy_slug:
                item = TaxonomyItem.objects.filter(
                    taxonomy__slug=taxonomy_slug,
                    name=value
                ).first()

                if not item and auto_create:
                    taxonomy = Taxonomy.objects.filter(slug=taxonomy_slug).first()
                    if not taxonomy:
                        taxonomy = Taxonomy.objects.create(
                            name=taxonomy_slug,
                            slug=taxonomy_slug,
                            description=f'自动创建的词汇表: {taxonomy_slug}'
                        )
                    item = TaxonomyItem.objects.create(
                        taxonomy=taxonomy,
                        name=value,
                        weight=0
                    )
            else:
                item = TaxonomyItem.objects.filter(name=value).first()
            return item

        try:
            if hasattr(fk_model_or_name, 'name'):
                return fk_model_or_name.objects.filter(name=value).first()
            elif hasattr(fk_model_or_name, 'customer_name'):
                return fk_model_or_name.objects.filter(customer_name=value).first()
        except Exception:
            pass

        return None
