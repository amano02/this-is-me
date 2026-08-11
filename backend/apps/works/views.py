from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View

from .models import Work
from .selectors import SORT_OPTIONS, filter_works, get_published_works_queryset
from .serializers import serialize_work_detail, serialize_work_list_item


class WorkListAPIView(View):
    """GET /api/works/?q=&genre=&sort=&page="""

    def get(self, request):
        q = request.GET.get("q", "").strip()
        genre_slug = request.GET.get("genre", "").strip()
        sort = request.GET.get("sort", "date_desc").strip()
        page = request.GET.get("page", "1")

        if sort not in SORT_OPTIONS:
            sort = "date_desc"

        queryset = filter_works(
            get_published_works_queryset(),
            q=q,
            genre_slug=genre_slug,
            sort=sort,
        )

        paginator = Paginator(queryset, 24)
        page_obj = paginator.get_page(page)

        return JsonResponse(
            {
                "count": paginator.count,
                "page": page_obj.number,
                "num_pages": paginator.num_pages,
                "results": [
                    serialize_work_list_item(work) for work in page_obj.object_list
                ],
            }
        )


class WorkDetailAPIView(View):
    """GET /api/works/<slug>/"""

    def get(self, request, slug):
        try:
            work = get_published_works_queryset().get(slug=slug)
        except Work.DoesNotExist:
            return JsonResponse({"error": "作品が見つかりません。"}, status=404)

        return JsonResponse(serialize_work_detail(work))
