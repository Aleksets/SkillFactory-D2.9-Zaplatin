from django.core.management.base import BaseCommand, CommandError
from ...models import Post, Category


class Command(BaseCommand):
    help = 'Удаление новостей в указанной категории'  # показывает подсказку при вводе "python manage.py <ваша команда> --help"
    missing_args_message = 'Вы не указали категорию категорию'
    # requires_migrations_checks = True  # напоминать ли о миграциях. Если тру — то будет напоминание о том, что не сделаны все миграции (если такие есть)

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('category',
                            nargs='+',
                            type=str,
                            help=f'Список категорий: {set(Category.objects.values_list("category_name", flat=True))}'
                            )

    def handle(self, *args, **options):
        # код, который выполнится при вызове команды
        # проверка наличия введенной(ых) категории(й)
        categories = set(Category.objects.values_list('category_name', flat=True))
        missed_categories = []
        for category in options['category']:
            if category not in categories:
                missed_categories.append(category)
        if len(missed_categories) > 0:
            self.stdout.write(
                self.style.ERROR(f'Категория(и) "{missed_categories}" отсутствует(ют)'))
            return
        self.stdout.readable()
        # спрашиваем пользователя, действительно ли он хочет удалить все новости в указанной категории
        self.stdout.write(f'Do you really want to delete all news in {options["category"]} category? Yes/no')
        answer = input()  # считываем подтверждение
        if answer == 'Yes':  # в случае подтверждения удаляем все новости в указанной категории
            for category in options["category"]:
                Post.objects.filter(category__category_name=category).delete()
            self.stdout.write(self.style.SUCCESS(f'Новости в категории(ях) {options["category"]} успешно удалены'))
            return
        self.stdout.write(
            self.style.ERROR('Вы не подтвердили удаление новостей'))  # в случае неправильного подтверждения, говорим что в доступе отказано
