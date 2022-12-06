from django import forms
from django.core.exceptions import ValidationError
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
                "title": "Заголовок должен быть не менее 20 символов!"
            })
        text = cleaned_data.get("text")
        if text == title:
            raise ValidationError({
                "text": "Текст не должен совпадать с заголовком!"
            })
        return cleaned_data
