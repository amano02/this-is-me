from django.db import models

from apps.works.models import Work


class ContactMessage(models.Model):
    """お問い合わせフォームの送信内容をDBに保存する。"""

    name = models.CharField("お名前", max_length=100)
    email = models.EmailField("メールアドレス")
    tel = models.CharField("電話番号", max_length=30, blank=True)
    message = models.TextField("メッセージ")
    related_work = models.ForeignKey(
        Work,
        verbose_name="関連する作品",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_messages",
    )
    is_read = models.BooleanField("既読", default=False)
    created_at = models.DateTimeField("送信日時", auto_now_add=True)

    class Meta:
        verbose_name = "お問い合わせ"
        verbose_name_plural = "お問い合わせ"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.created_at:%Y-%m-%d %H:%M})"
