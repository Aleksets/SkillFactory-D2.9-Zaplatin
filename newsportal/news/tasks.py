from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст
from django.utils import timezone
from .models import Post, Category
import re


@shared_task
def send_email(username, category, title, text, pk, email):
    # получаем наш html
    html_content = render_to_string(
        'new_post_email.html',
        {
            'username': username,
            'category': category,
            'title': title,
            'text': text,
            'link': f'{settings.SITE_URL}/news/',
            'pk': pk,
        }
    )
    # конструктор письма
    msg = EmailMultiAlternatives(
        # тема
        subject=f'{title}',
        # текст
        body='',
        # от
        from_email=settings.DEFAULT_FROM_EMAIL,
        # кому (список)
        to=[email],
    )
    # заменяем body на html_content
    msg.attach_alternative(html_content, "text/html")
    # отсылаем
    msg.send()


@shared_task
def week_posts_email():
    regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]"
                       r"+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]"
                       r"+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
    # вычтем от сегодняшнего дня 7 дней (начало диапазона новостей по дате)
    last_week = timezone.now() - timezone.timedelta(7)
    posts = Post.objects.filter(add_date__gte=last_week)
    category = set(posts.values_list('category__category_name', flat=True))
    for new_post_category in Category.objects.all():
        if new_post_category.category_name in category:
            for user_to_email in new_post_category.subscribers.all():
                if re.fullmatch(regex, user_to_email.email):
                    # получаем наш html
                    html_content = render_to_string(
                        'week_posts_email.html',
                        {
                            'username': user_to_email.username,
                            'category': new_post_category,
                            'posts': posts,
                            'link': f'{settings.SITE_URL}/news/',
                        }
                    )
                    # конструктор письма
                    msg = EmailMultiAlternatives(
                        # тема
                        subject='Новости за прошедшую неделю',
                        # текст
                        body='',
                        # от
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        # кому (список)
                        to=[user_to_email.email],
                    )
                    # заменяем body на html_content
                    msg.attach_alternative(html_content, "text/html")
                    # отсылаем
                    msg.send()
