from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Post, Author
from .filters import PostFilter
from .forms import PostForm
from django.core.exceptions import PermissionDenied


class NewsList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-add_date'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'news.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'news'
    paginate_by = 10  # вот так мы можем указать количество записей на странице


class PostDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельной новости/статье
    model = Post
    # Используем другой шаблон — post.html
    template_name = 'post.html'


class NewsSearch(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-add_date'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'news_search.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'news_search'
    paginate_by = 10  # вот так мы можем указать количество записей на странице

    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        # С помощью super() мы обращаемся к родительским классам
        # и вызываем у них метод get_context_data с теми же аргументами,
        # что и были переданы нам.
        # В ответе мы должны получить словарь.
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        return context


# Добавляем новое представление для публикации новости.
class PostCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    raise_exception = True
    permission_required = ('news.add_post',)
    # Указываем нашу разработанную форму
    form_class = PostForm
    # модель новостей
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'post_edit.html'
    # context_object_name = 'post_create'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # Добавляем текущего пользователя в форму
        self.object.author = Author.objects.get(author=self.request.user)
        self.object.save()
        return super().form_valid(form)


# Добавляем представление для изменения новости/статьи.
class PostUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    raise_exception = True
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    # Проверяем, является ли авторизованный пользователь автором статьи,
    # которую он пытается изменить.
    # Если да, то позволяем ему изменять статью,
    # Если нет - переносим его на 403.html
    def get_object(self, queryset=None):
        obj = UpdateView.get_object(self, queryset=None)
        if not obj.author.author == self.request.user:
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # Добавляем текущего пользователя в форму
        self.object.author = Author.objects.get(author=self.request.user)
        self.object.save()
        return super().form_valid(form)


# Представление, удаляющее новость/статью.
class PostDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    raise_exception = True
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news')
    # context_object_name = 'post_delete'
