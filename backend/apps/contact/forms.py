from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "tel", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"id": "name", "size": "60"}),
            "email": forms.EmailInput(attrs={"id": "email", "size": "60"}),
            "tel": forms.TextInput(attrs={"id": "tel", "size": "60"}),
            "message": forms.Textarea(attrs={"id": "msg", "cols": "50", "rows": "5"}),
        }
