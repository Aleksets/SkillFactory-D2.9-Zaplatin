from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache  # импортируем наш кэш
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _ # импортируем функцию для перевода
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http.response import HttpResponse #  импортируем респонс для проверки текста

from .filters import PostFilter
from .forms import PostForm
from .models import Post, Author, Category

import pytz  # импортируем стандартный модуль для работы с часовыми поясами

my_timezones = {
    'Europe/Moscow': 'Europe/Moscow',
    'Europe/Paris': 'Europe/Paris',
    'America/New_York': 'America/New_York',
}


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

    # def get(self, request):
    #     # .  Translators: This message appears on the home page only
    #     models = Post.objects.all()
    #     context = {
    #         'models': models,
    #         'current_time': timezone.now(),
    #         'timezones': my_timezones  # добавляем в контекст нужные часовые пояса
    #     }
    #     return HttpResponse(render(request, 'news.html', context))
    #
    def get_context_data(self, **kwargs):
        current_time = timezone.localtime(timezone.now())
        context = super().get_context_data(**kwargs)
        context['current_time'] = current_time
        context['timezones'] = my_timezones
        # здесь дописываем свои данные при наличии
        return context

    #  по пост-запросу будем добавлять в сессию часовой пояс, который и будет обрабатываться написанным нами ранее middleware
    def post(self, request):
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('news')


class PostDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельной новости/статье
    model = Post
    # Используем шаблон post.html
    template_name = 'post.html'

    # переопределяем метод получения объекта
    def get_object(self, *args, **kwargs):
        # кэш очень похож на словарь, и метод get действует так же.
        # Он забирает значение по ключу, если его нет, то забирает None.
        obj = cache.get(f'post-{self.kwargs["pk"]}', None)
        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)
        return obj


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        limit = settings.DAILY_POST_LIMIT
        prev_day = timezone.now() - timezone.timedelta(days=1)
        posts_day_count = Post.objects.filter(add_date__gte=prev_day, author__author=self.request.user).count()
        if limit <= posts_day_count:
            context['post_limit'] = True
        return context


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


@login_required
def subscribe(request, pk1, pk2):
    post = Post.objects.get(id=pk1)
    user = request.user
    category = Category.objects.get(id=pk2)
    category.subscribers.add(user)
    message = _('You have successfully subscribed to the newsletter in the category')
    return render(request, 'subscribe.html', {'post': post, 'category': category, 'message': message})


@login_required
def unsubscribe(request, pk1, pk2):
    post = Post.objects.get(id=pk1)
    user = request.user
    category = Category.objects.get(id=pk2)
    category.subscribers.remove(user)
    message = _('You have successfully unsubscribed from the newsletter in the category')
    return render(request, 'unsubscribe.html', {'post': post, 'category': category, 'message': message})
