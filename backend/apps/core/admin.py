from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from .models import HeroSlide, SiteProfile, SnsLink


class SnsLinkInline(admin.TabularInline):
    model = SnsLink
    extra = 1
    fields = ("platform", "url", "display_order")
    ordering = ("display_order",)


@admin.register(SiteProfile)
class SiteProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "role_title", "updated_at")
    inlines = [SnsLinkInline]

    def has_add_permission(self, request):
        # SiteProfileは1件のみ運用する
        if SiteProfile.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(HeroSlide)
class HeroSlideAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("caption", "is_published", "display_order")
    list_filter = ("is_published",)
