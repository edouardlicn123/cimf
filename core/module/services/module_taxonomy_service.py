import logging

from core.models import Taxonomy, TaxonomyItem
from core.module.models import Module

logger = logging.getLogger(__name__)


class ModuleTaxonomyService:

    @staticmethod
    def create_module_taxonomies(module: Module) -> int:
        from core.module.services.module_registry_service import ModuleRegistryService  # noqa: PLC0415
        module_info = ModuleRegistryService._load_module_info(module.path)
        if not module_info:
            return 0

        taxonomies = module_info.get("taxonomies", [])
        if not taxonomies:
            return 0

        created_count = 0
        slugs = [t.get("slug") for t in taxonomies if t.get("slug") and t.get("name")]
        existing_taxonomies = {t.slug: t for t in Taxonomy.objects.filter(slug__in=slugs)}
        existing_items = {
            (item.taxonomy_id, item.name): item for item in TaxonomyItem.objects.filter(taxonomy__slug__in=slugs)
        }

        items_to_create = []
        new_taxonomies = []

        for tax_data in taxonomies:
            slug = tax_data.get("slug")
            name = tax_data.get("name")
            items = tax_data.get("items", [])

            if not slug or not name:
                continue

            existing = existing_taxonomies.get(slug)
            if existing:
                items_to_create.extend(
                    TaxonomyItem(taxonomy=existing, name=item_name, weight=0)
                    for item_name in items
                    if (existing.id, item_name) not in existing_items
                )
                continue

            taxonomy = Taxonomy(name=name, slug=slug, description=f"{module.name} 模块词汇表")
            new_taxonomies.append(taxonomy)

        Taxonomy.objects.bulk_create(new_taxonomies, ignore_conflicts=True)
        new_slugs = [t.slug for t in new_taxonomies]
        created_taxonomies = {t.slug: t for t in Taxonomy.objects.filter(slug__in=new_slugs)}

        for tax_data in taxonomies:
            slug = tax_data.get("slug")
            items = tax_data.get("items", [])

            if slug in created_taxonomies:
                taxonomy = created_taxonomies[slug]
                for idx, item_name in enumerate(items):
                    items_to_create.append(TaxonomyItem(taxonomy=taxonomy, name=item_name, weight=idx))
                created_count += 1

        if items_to_create:
            TaxonomyItem.objects.bulk_create(items_to_create, ignore_conflicts=True)

        all_taxonomies = {**existing_taxonomies, **created_taxonomies}
        for tax_data in taxonomies:
            slug = tax_data.get("slug")
            name = tax_data.get("name")
            items = tax_data.get("items", [])

            if not slug or not name:
                continue

            taxonomy = all_taxonomies.get(slug)
            if not taxonomy:
                raise RuntimeError(f"词汇表创建失败: {slug}")

            existing_item_names = {
                name for (tid, name) in existing_items if tid == taxonomy.id
            }
            expected_items = set(items)
            missing_items = expected_items - existing_item_names

            if missing_items:
                logger.warning("词汇表 %s 缺少项目: %s，尝试补充", slug, missing_items)
                for item_name in missing_items:
                    TaxonomyItem.objects.create(taxonomy=taxonomy, name=item_name, weight=0)

        return created_count
