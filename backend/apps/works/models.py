from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Genre(models.Model):
    """作品のジャンル（illustration, 3dcg, music, others など）。管理画面から自由に追加可能。"""

    name = models.CharField("ジャンル名", max_length=100, unique=True)
    slug = models.SlugField("スラッグ", max_length=120, unique=True, blank=True)
    description = models.TextField("説明", blank=True)
    background_image = models.ImageField(
        "背景画像", upload_to="works/genres/bg/", blank=True
    )
    display_order = models.PositiveIntegerField("表示順", default=0)
    is_published = models.BooleanField("公開する", default=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "ジャンル"
        verbose_name_plural = "ジャンル"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """自由に付与できるタグ（作品の雰囲気・技法など）。"""

    name = models.CharField("タグ名", max_length=50, unique=True)
    slug = models.SlugField("スラッグ", max_length=60, unique=True, blank=True)

    class Meta:
        verbose_name = "タグ"
        verbose_name_plural = "タグ"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class WorkTool(models.Model):
    """使用ツール（Illustrator, Blender, Photoshop など）。"""

    name = models.CharField("ツール名", max_length=50, unique=True)

    class Meta:
        verbose_name = "使用ツール"
        verbose_name_plural = "使用ツール"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Work(models.Model):
    """作品本体。検索・並び替え・複数メディアに対応するための中心モデル。"""

    class Status(models.TextChoices):
        DRAFT = "draft", "下書き"
        PUBLISHED = "published", "公開"

    genre = models.ForeignKey(
        Genre, verbose_name="ジャンル", on_delete=models.PROTECT, related_name="works"
    )
    title = models.CharField("作品名", max_length=200)
    slug = models.SlugField("スラッグ", max_length=220, unique=True, blank=True)
    description = models.TextField("作品解説", blank=True)
    highlights = models.TextField(
        "見どころ", blank=True, help_text="1行1項目で入力してください。"
    )
    created_date = models.DateField("制作日", null=True, blank=True)
    production_hours = models.PositiveIntegerField(
        "制作時間（時間）", null=True, blank=True
    )
    tools = models.ManyToManyField(WorkTool, verbose_name="使用ツール", blank=True)
    tags = models.ManyToManyField(Tag, verbose_name="タグ", blank=True)
    status = models.CharField(
        "ステータス", max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    is_featured = models.BooleanField("おすすめ表示", default=False)
    display_order = models.PositiveIntegerField("表示順", default=0)
    view_count = models.PositiveIntegerField("閲覧数", default=0, editable=False)
    published_at = models.DateTimeField("公開日時", null=True, blank=True)
    created_at = models.DateTimeField("登録日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "作品"
        verbose_name_plural = "作品"
        ordering = ["display_order", "-published_at", "-created_date"]
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["genre", "status"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True) or "work"
            slug = base_slug
            n = 1
            while Work.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base_slug}-{n}"
            self.slug = slug
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("works:detail", kwargs={"slug": self.slug})

    @property
    def highlights_list(self):
        return [line.strip() for line in self.highlights.splitlines() if line.strip()]

    @property
    def primary_media(self):
        return self.media.filter(is_primary=True).first() or self.media.first()


class WorkMedia(models.Model):
    """作品に紐づく複数メディア（画像・動画・音声・外部埋め込み・PDF等）。"""

    class MediaType(models.TextChoices):
        IMAGE = "image", "画像"
        VIDEO = "video", "動画"
        AUDIO = "audio", "音声"
        EMBED = "embed", "外部埋め込み(YouTube等)"
        DOCUMENT = "document", "ドキュメント(PDF等)"

    work = models.ForeignKey(
        Work, verbose_name="作品", on_delete=models.CASCADE, related_name="media"
    )
    media_type = models.CharField(
        "メディア種別", max_length=20, choices=MediaType.choices
    )
    file = models.FileField(
        "ファイル", upload_to="works/media/%Y/%m/", blank=True
    )
    external_url = models.URLField(
        "外部URL",
        blank=True,
        help_text="YouTube/SoundCloud等の埋め込みURL。外部埋め込みの場合はこちらを使用。",
    )
    caption = models.CharField("キャプション", max_length=200, blank=True)
    display_order = models.PositiveIntegerField("表示順", default=0)
    is_primary = models.BooleanField(
        "サムネイルにする", default=False, help_text="一覧表示のサムネイルとして使用します。"
    )
    created_at = models.DateTimeField("登録日時", auto_now_add=True)

    class Meta:
        verbose_name = "作品メディア"
        verbose_name_plural = "作品メディア"
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.work.title} - {self.get_media_type_display()}"

    def clean(self):
        if self.media_type == self.MediaType.EMBED and not self.external_url:
            raise ValidationError("外部埋め込みの場合はURLを入力してください。")
        if self.media_type != self.MediaType.EMBED and not self.file and not self.external_url:
            raise ValidationError("ファイルまたは外部URLのいずれかを入力してください。")
