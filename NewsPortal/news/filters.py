from django_filters import FilterSet, ModelMultipleChoiceFilter, DateFilter
from django.forms import DateInput
from .models import Post, Category


# Создаем свой набор фильтров для модели Post.
class PostFilter(FilterSet):
    # поиск по категории
    category = ModelMultipleChoiceFilter(
        field_name='postcategory__category',
        queryset=Category.objects.all(),
        label='Категория',
    )
    # позже указанной даты
    added_after = DateFilter(
        field_name='add_date',
        lookup_expr='gt',
        widget=DateInput(
            format='%d.%m.%Y',
            attrs={'type': 'date'},
        ),
        label='Позже указанной даты',
    )

    class Meta:
        # В Meta классе мы должны указать Django модель,
        # в которой будем фильтровать записи.
        model = Post
        # В fields мы описываем по каким полям модели
        # будет производиться фильтрация.
        fields = {
            # название содержит
            'title': ['icontains'],
        }
