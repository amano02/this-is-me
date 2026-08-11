from django.core.exceptions import ValidationError
from django.db import models


class SiteProfile(models.Model):
    """サイト全体のプロフィール情報。1レコードのみ運用するシングルトン的モデル。"""

    display_name = models.CharField("表示名", max_length=100)
    role_title = models.CharField(
        "肩書き", max_length=100, blank=True, help_text="例: multi creator"
    )
    birth_place = models.CharField("出身地", max_length=100, blank=True)
    birthday = models.DateField("誕生日", null=True, blank=True)
    school = models.CharField("学校", max_length=200, blank=True)
    bio = models.TextField("自己紹介", blank=True)
    avatar = models.ImageField("プロフィール画像", upload_to="core/profile/", blank=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "サイトプロフィール"
        verbose_name_plural = "サイトプロフィール"

    def __str__(self):
        return self.display_name

    def clean(self):
        if not self.pk and SiteProfile.objects.exists():
            raise ValidationError("サイトプロフィールは1件のみ登録できます。既存のレコードを編集してください。")


class SnsLink(models.Model):
    class Platform(models.TextChoices):
        INSTAGRAM = "instagram", "Instagram"
        TWITTER = "twitter", "X (Twitter)"
        FACEBOOK = "facebook", "Facebook"
        YOUTUBE = "youtube", "YouTube"
        OTHER = "other", "その他"

    profile = models.ForeignKey(
        SiteProfile, on_delete=models.CASCADE, related_name="sns_links"
    )
    platform = models.CharField("プラットフォーム", max_length=20, choices=Platform.choices)
    url = models.URLField("URL")
    display_order = models.PositiveIntegerField("表示順", default=0)

    class Meta:
        verbose_name = "SNSリンク"
        verbose_name_plural = "SNSリンク"
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.get_platform_display()}: {self.url}"


class HeroSlide(models.Model):
    """トップページのフルスクリーンスライダー（Vegas）用の画像。"""

    caption = models.CharField("キャプション", max_length=200, blank=True)
    image_pc = models.ImageField("PC用画像", upload_to="core/hero/pc/")
    image_sp = models.ImageField(
        "スマートフォン用画像", upload_to="core/hero/sp/", blank=True
    )
    display_order = models.PositiveIntegerField("表示順", default=0)
    is_published = models.BooleanField("公開する", default=True)

    class Meta:
        verbose_name = "ヒーロースライド"
        verbose_name_plural = "ヒーロースライド"
        ordering = ["display_order"]

    def __str__(self):
        return self.caption or f"Slide #{self.pk}"
