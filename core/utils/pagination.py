"""通用分页工具函数"""

from django.core.paginator import Paginator


def paginate_queryset(request, queryset, per_page=10):
    try:
        page_num = int(request.GET.get("page", 1))
        page_num = max(page_num, 1)
    except (ValueError, TypeError):
        page_num = 1

    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_num)

    current = page_obj.number
    total = paginator.num_pages
    if total == 0:
        page_range = range(0)
    else:
        start = max(1, current - 2)
        end = min(total, current + 2)
        page_range = range(start, end + 1)

    return page_obj, page_range
