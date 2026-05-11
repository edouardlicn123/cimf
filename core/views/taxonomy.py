"""
词汇表视图模块
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.decorators import admin_required
from core.models import Taxonomy, TaxonomyItem
from core.services import TaxonomyService
from core.utils.pagination import paginate_queryset


@admin_required
def taxonomies(request):
    """词汇表列表"""
    search = request.GET.get('search', '').strip()

    queryset = Taxonomy.objects.all()
    if search:
        queryset = queryset.filter(name__icontains=search)

    page_ctx = paginate_queryset(request, queryset, per_page=10)

    return render(request, 'structure/taxonomies/index.html', {
        'taxonomies': page_ctx['page_obj'].object_list,
        **page_ctx,
        'active_section': 'taxonomies',
        'search': search,
    })


@admin_required
def taxonomy_create(request):
    """创建词汇表"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        description = request.POST.get('description', '').strip()

        if not name or not slug:
            messages.error(request, '名称和标识不能为空')
            return redirect('core:taxonomies')

        Taxonomy.objects.create(
            name=name,
            slug=slug,
            description=description
        )
        messages.success(request, '词汇表创建成功')
        return redirect('core:taxonomies')

    return render(request, 'structure/taxonomies/edit.html', {
        'taxonomy': None,
        'active_section': 'taxonomies',
    })


@admin_required
def taxonomy_view(request, taxonomy_id: int):
    """查看词汇表"""
    taxonomy = get_object_or_404(Taxonomy, id=taxonomy_id)

    queryset = taxonomy.items.all().order_by('weight', 'name')
    page_ctx = paginate_queryset(request, queryset, per_page=10)

    return render(request, 'structure/taxonomies/view.html', {
        'taxonomy': taxonomy,
        'items': page_ctx['page_obj'].object_list,
        **page_ctx,
        'active_section': 'taxonomies',
    })


@admin_required
def taxonomy_edit(request, taxonomy_id: int):
    """编辑词汇表"""
    taxonomy = get_object_or_404(Taxonomy, id=taxonomy_id)

    if request.method == 'POST':
        taxonomy.name = request.POST.get('name', '').strip()
        taxonomy.slug = request.POST.get('slug', '').strip()
        taxonomy.description = request.POST.get('description', '').strip()

        if not taxonomy.name or not taxonomy.slug:
            messages.error(request, '名称和标识不能为空')
            return redirect('core:taxonomy_edit', taxonomy_id)

        taxonomy.save()

        messages.success(request, '词汇表更新成功')
        return redirect('core:taxonomies')

    return render(request, 'structure/taxonomies/edit.html', {
        'taxonomy': taxonomy,
        'active_section': 'taxonomies',
    })


@admin_required
@require_POST
def taxonomy_delete(request, taxonomy_id: int):
    """删除词汇表"""
    taxonomy = get_object_or_404(Taxonomy, id=taxonomy_id)
    taxonomy.delete()
    messages.success(request, '词汇表已删除')
    return redirect('core:taxonomies')


@admin_required
def taxonomy_item_create(request, taxonomy_id: int):
    """创建词汇项"""
    get_object_or_404(Taxonomy, id=taxonomy_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if name:
            TaxonomyService.create_item(taxonomy_id, name, description)
            messages.success(request, '词汇项创建成功')

        return redirect('core:taxonomy_view', taxonomy_id)

    return redirect('core:taxonomy_view', taxonomy_id)


@admin_required
def taxonomy_item_update(request, taxonomy_id: int, item_id: int):
    """更新词汇项"""
    get_object_or_404(Taxonomy, id=taxonomy_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if name:
            item = TaxonomyItem.objects.filter(id=item_id, taxonomy_id=taxonomy_id).first()
            # 调用者已检查 None
            if item:
                TaxonomyService.update_item(item_id, name=name, description=description)
                messages.success(request, '词汇项更新成功')
            else:
                messages.error(request, '词汇项不存在或不属于当前词汇表')

        return redirect('core:taxonomy_view', taxonomy_id)

    return redirect('core:taxonomy_view', taxonomy_id)


@admin_required
@require_POST
def taxonomy_item_delete(request, taxonomy_id: int, item_id: int):
    """删除词汇项"""
    item = TaxonomyItem.objects.filter(id=item_id, taxonomy_id=taxonomy_id).first()
    if item:
        TaxonomyService.delete_item(item_id)
        messages.success(request, '词汇项已删除')
    else:
        messages.error(request, '词汇项不存在或不属于当前词汇表')
    return redirect('core:taxonomy_view', taxonomy_id)
