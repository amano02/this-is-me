from .models import SiteProfile


def site_profile(request):
    """全テンプレートで `site_profile` としてプロフィールを参照できるようにする。"""
    profile = SiteProfile.objects.prefetch_related("sns_links").first()
    return {"site_profile": profile}
