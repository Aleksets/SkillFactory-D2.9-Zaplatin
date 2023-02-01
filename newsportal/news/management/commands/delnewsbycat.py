from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _ # импортируем функцию для перевода
from ...models import Post, Category


class Command(BaseCommand):
    help = _('Delete news in the specified category')  # показывает подсказку при вводе "python manage.py <ваша команда> --help"
    missing_args_message = _("You didn't specify a category")
    # requires_migrations_checks = True  # напоминать ли о миграциях. Если тру — то будет напоминание о том, что не сделаны все миграции (если такие есть)

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('category',
                            nargs='+',
                            type=str,
                            help=_('List of categories') + f': {set(Category.objects.values_list("category_name", flat=True))}'
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
                self.style.ERROR(_('Category(s)') + f'{missed_categories}' + _('absent')))
            return
        self.stdout.readable()
        # спрашиваем пользователя, действительно ли он хочет удалить все новости в указанной категории
        self.stdout.write(_('Do you really want to delete all news in') + f'{options["category"]}' +
                          _('category? Yes/no'))
        answer = input()  # считываем подтверждение
        if answer == _('Yes'):  # в случае подтверждения удаляем все новости в указанной категории
            for category in options["category"]:
                Post.objects.filter(category__category_name=category).delete()
            self.stdout.write(self.style.SUCCESS(_('News in category(s)') + f'{options["category"]}' +
                                                 _('removed successfully')))
            return
        self.stdout.write(
            self.style.ERROR(_('You have not confirmed the deletion of news')))  # в случае неправильного подтверждения, говорим что в доступе отказано
