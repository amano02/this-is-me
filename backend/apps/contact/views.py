from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import View

from .forms import ContactForm


class ContactCreateView(View):
    """トップページのお問い合わせフォームからのPOSTを受け付ける。"""

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "お問い合わせを受け付けました。ご連絡ありがとうございます。")
            return redirect(f"{reverse('core:index')}#form")

        messages.error(request, "入力内容に誤りがあります。もう一度ご確認ください。")
        # バリデーションエラー時は入力内容を保持したままトップページを再表示する。
        from apps.core.views import IndexView

        view = IndexView()
        view.request = request
        view.args = args
        view.kwargs = {**kwargs, "contact_form": form}
        context = view.get_context_data(**view.kwargs)
        return view.render_to_response(context)
