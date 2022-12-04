from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст
from django.utils import timezone
from ...models import Post, Category

import logging
import re

logger = logging.getLogger(__name__)


# наша задача по выводу текста на экран
def my_job():
    #  Your job processing logic here...
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


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="mon", hour="08", minute="00"),
            # То же, что и интервал, но задача триггера
            # таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи,
            # которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
