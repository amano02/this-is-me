from adminsortable2.admin import SortableAdminMixin, SortableTabularInline
from django.contrib import admin

from .models import Genre, Tag, Work, WorkMedia, WorkTool


class WorkMediaInline(SortableTabularInline):
    model = WorkMedia
    extra = 1
    fields = (
        "media_type",
        "file",
        "external_url",
        "caption",
        "is_primary",
        "display_order",
    )


@admin.register(Genre)
class GenreAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "is_published", "display_order", "work_count")
    list_filter = ("is_published",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="作品数")
    def work_count(self, obj):
        return obj.works.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(WorkTool)
class WorkToolAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Work)
class WorkAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "genre",
        "status",
        "is_featured",
        "created_date",
        "published_at",
        "view_count",
    )
    list_filter = ("genre", "status", "is_featured", "tags", "tools", "created_date")
    search_fields = ("title", "description", "tags__name", "tools__name")
    autocomplete_fields = ("tags", "tools")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_date"
    readonly_fields = ("view_count", "created_at", "updated_at")
    inlines = [WorkMediaInline]
    fieldsets = (
        (None, {"fields": ("genre", "title", "slug", "status", "is_featured")}),
        (
            "作品情報",
            {
                "fields": (
                    "description",
                    "highlights",
                    "created_date",
                    "production_hours",
                    "tools",
                    "tags",
                )
            },
        ),
        (
            "公開設定",
            {"fields": ("display_order", "published_at")},
        ),
        (
            "メタ情報",
            {
                "classes": ("collapse",),
                "fields": ("view_count", "created_at", "updated_at"),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("genre").prefetch_related("tags", "tools")
