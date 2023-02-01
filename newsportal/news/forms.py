from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _ # импортируем функцию для перевода
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'kind',
            'category',
            'title',
            'text',
        ]

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        if title is not None and len(title) < 20:
            raise ValidationError({
                "title": _("Title must be at least 20 characters!")
            })
        text = cleaned_data.get("text")
        if text == title:
            raise ValidationError({
                "text": _("The text must not match the title!")
            })
        return cleaned_data
