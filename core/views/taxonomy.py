"""词汇表视图模块"""

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.decorators import admin_required
from core.models import Taxonomy, TaxonomyItem
from core.services import TaxonomyService
from core.utils.pagination import paginate_queryset
from core.utils.views import redirect_with_error, redirect_with_success


def _get_taxonomy_or_error(taxonomy_id):
    return get_object_or_404(Taxonomy, id=taxonomy_id)


def _handle_taxonomy_form(request, taxonomy=None):
    name = request.POST.get("name", "").strip()
    slug = request.POST.get("slug", "").strip()
    description = request.POST.get("description", "").strip()

    if not name or not slug:
        redirect_url = "core:taxonomy_edit" if taxonomy else "core:taxonomies"
        args = (taxonomy.id,) if taxonomy else ()
        return redirect_with_error(request, "名称和标识不能为空", redirect_url, *args)

    if taxonomy:
        if TaxonomyService.check_slug_exists_exclude(slug, taxonomy.id):
            return redirect_with_error(request, f"标识 '{slug}' 已被使用", "core:taxonomy_edit", taxonomy.id)
        taxonomy.name = name
        taxonomy.slug = slug
        taxonomy.description = description
        taxonomy.save()
        return redirect_with_success(request, "词汇表更新成功", "core:taxonomies")

    if TaxonomyService.check_slug_exists(slug):
        return redirect_with_error(request, f"标识 '{slug}' 已被使用", "core:taxonomies")
    TaxonomyService.create_taxonomy(name, slug, description)
    return redirect_with_success(request, "词汇表创建成功", "core:taxonomies")


def _handle_taxonomy_item_form(request, taxonomy_id, item_id=None):
    name = request.POST.get("name", "").strip()
    description = request.POST.get("description", "").strip()

    if not name:
        return redirect("core:taxonomy_view", taxonomy_id)

    if item_id:
        item = TaxonomyItem.objects.filter(id=item_id, taxonomy_id=taxonomy_id).first()
        if not item:
            return redirect_with_error(request, "词汇项不存在或不属于当前词汇表", "core:taxonomy_view", taxonomy_id)
        TaxonomyService.update_item(item_id, name=name, description=description)
        return redirect_with_success(request, "词汇项更新成功", "core:taxonomy_view", taxonomy_id)

    TaxonomyService.create_item(taxonomy_id, name, description)
    return redirect_with_success(request, "词汇项创建成功", "core:taxonomy_view", taxonomy_id)


@admin_required
def taxonomies(request):
    """词汇表列表"""
    search = request.GET.get("search", "").strip()
    queryset = TaxonomyService.get_taxonomy_list(search)
    page_obj, page_range = paginate_queryset(request, queryset, per_page=10)
    return render(
        request,
        "structure/taxonomies/index.html",
        {
            "taxonomies": page_obj.object_list,
            "page_obj": page_obj,
            "page_range": page_range,
            "active_section": "taxonomies",
            "search": search,
        },
    )


@admin_required
def taxonomy_create(request):
    """创建词汇表"""
    if request.method == "POST":
        return _handle_taxonomy_form(request)
    return render(
        request,
        "structure/taxonomies/edit.html",
        {"taxonomy": None, "active_section": "taxonomies"},
    )


@admin_required
def taxonomy_view(request, taxonomy_id: int):
    """查看词汇表"""
    taxonomy = _get_taxonomy_or_error(taxonomy_id)
    queryset = TaxonomyService.get_items(taxonomy_id)
    page_obj, page_range = paginate_queryset(request, queryset, per_page=10)
    return render(
        request,
        "structure/taxonomies/view.html",
        {
            "taxonomy": taxonomy,
            "items": page_obj.object_list,
            "page_obj": page_obj,
            "page_range": page_range,
            "active_section": "taxonomies",
        },
    )


@admin_required
def taxonomy_edit(request, taxonomy_id: int):
    """编辑词汇表"""
    taxonomy = _get_taxonomy_or_error(taxonomy_id)
    if request.method == "POST":
        return _handle_taxonomy_form(request, taxonomy)
    return render(
        request,
        "structure/taxonomies/edit.html",
        {"taxonomy": taxonomy, "active_section": "taxonomies"},
    )


@admin_required
@require_POST
def taxonomy_delete(request, taxonomy_id: int):
    """删除词汇表"""
    taxonomy = _get_taxonomy_or_error(taxonomy_id)
    taxonomy.delete()
    return redirect_with_success(request, "词汇表已删除", "core:taxonomies")


@admin_required
def taxonomy_item_create(request, taxonomy_id: int):
    """创建词汇项"""
    _get_taxonomy_or_error(taxonomy_id)
    if request.method == "POST":
        return _handle_taxonomy_item_form(request, taxonomy_id)
    return redirect("core:taxonomy_view", taxonomy_id)


@admin_required
def taxonomy_item_update(request, taxonomy_id: int, item_id: int):
    """更新词汇项"""
    _get_taxonomy_or_error(taxonomy_id)
    if request.method == "POST":
        return _handle_taxonomy_item_form(request, taxonomy_id, item_id)
    return redirect("core:taxonomy_view", taxonomy_id)


@admin_required
@require_POST
def taxonomy_item_delete(request, taxonomy_id: int, item_id: int):
    """删除词汇项"""
    item = TaxonomyItem.objects.filter(id=item_id, taxonomy_id=taxonomy_id).first()
    if item:
        TaxonomyService.delete_item(item_id)
        return redirect_with_success(request, "词汇项已删除", "core:taxonomy_view", taxonomy_id)
    return redirect_with_error(request, "词汇项不存在或不属于当前词汇表", "core:taxonomy_view", taxonomy_id)
