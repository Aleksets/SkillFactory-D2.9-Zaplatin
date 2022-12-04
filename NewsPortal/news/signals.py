from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст
from .models import PostCategory
import re


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


@receiver(m2m_changed, sender=PostCategory)
def new_post_email(instance, **kwargs):
    if kwargs['action'] == 'post_add':
        regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]"
                           r"+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]"
                           r"+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
        for new_post_category in instance.category.all():
            for user_to_email in new_post_category.subscribers.all():
                if re.fullmatch(regex, user_to_email.email):
                    send_email(user_to_email.username, new_post_category, instance.title,
                               instance.text, instance.pk, user_to_email.email)
