from django.db.models import Q

from .models import Work


SORT_OPTIONS = {
    "date_desc": ("-published_at", "-created_date", "display_order"),
    "date_asc": ("published_at", "created_date", "display_order"),
    "title": ("title",),
    "featured": ("-is_featured", "display_order", "-published_at"),
}


def get_published_works_queryset():
    return (
        Work.objects.filter(status=Work.Status.PUBLISHED)
        .select_related("genre")
        .prefetch_related("media", "tags", "tools")
    )


def filter_works(queryset, *, q="", genre_slug="", sort="date_desc"):
    if genre_slug:
        queryset = queryset.filter(genre__slug=genre_slug, genre__is_published=True)

    if q:
        queryset = queryset.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(tags__name__icontains=q)
        ).distinct()

    ordering = SORT_OPTIONS.get(sort, SORT_OPTIONS["date_desc"])
    return queryset.order_by(*ordering)
