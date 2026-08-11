from django.views.generic import TemplateView

from apps.contact.forms import ContactForm
from apps.works.models import Genre

from .models import HeroSlide


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genres = (
            Genre.objects.filter(is_published=True)
            .prefetch_related("works__media", "works__tags", "works__tools")
        )
        # 公開済みの作品のみに絞り込んだジャンルを渡す（未公開作品しかないジャンルも表示自体は維持）
        for genre in genres:
            genre.published_works = [
                work for work in genre.works.all() if work.status == work.Status.PUBLISHED
            ]

        context["genres"] = genres
        context["hero_slides"] = HeroSlide.objects.filter(is_published=True)
        context["contact_form"] = kwargs.get("contact_form") or ContactForm()
        return context
