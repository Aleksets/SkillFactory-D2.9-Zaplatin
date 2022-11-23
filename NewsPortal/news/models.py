from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.


# Модель Author
# Модель, содержащая объекты всех авторов.
# Имеет следующие поля:
# - связь «один к одному» с встроенной моделью пользователей User;
# - рейтинг пользователя.
class Author(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    rate = models.IntegerField(default=0)

    # Метод update_rating() обновляет рейтинг пользователя.
    # Он состоит из:
    # - суммарного рейтинга каждой статьи автора, умноженного на 3;
    # - суммарного рейтинга всех комментариев автора;
    # - суммарного рейтинга всех комментариев к статьям автора.
    def update_rating(self):
        post_rate = sum(Post.objects.filter(author=self).values_list('rate', flat=True))
        comment_rate = sum(Comment.objects.filter(author__author=self).values_list('rate', flat=True))
        post_comment_rate = sum(Comment.objects.filter(post__in=Post.objects.filter(author=self)).
                                values_list('rate', flat=True))
        self.rate = 3 * post_rate + comment_rate + post_comment_rate
        self.save()

    def __str__(self):
        return self.author.username


# Модель Category
# Категории новостей/статей — темы, которые они отражают (спорт, политика, образование и т. д.).
# Имеет единственное поле: название категории.
# Поле должно быть уникальным (в определении поля необходимо написать параметр unique = True).
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.category_name


# Модель Post
# Эта модель должна содержать в себе статьи и новости, которые создают пользователи.
# Каждый объект может иметь одну или несколько категорий.
# Соответственно, модель должна включать следующие поля:
# связь «один ко многим» с моделью Author;
# поле с выбором — «статья» или «новость»;
# автоматически добавляемая дата и время создания;
# связь «многие ко многим» с моделью Category (с дополнительной моделью PostCategory);
# заголовок статьи/новости;
# текст статьи/новости;
# рейтинг статьи/новости.
POST_KINDS = [
    ('AR', 'Статья'),
    ('NE', 'Новость')
]


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    kind = models.CharField(max_length=2, choices=POST_KINDS)
    add_date = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rate = models.IntegerField(default=0)

    # Методы like() и dislike() увеличивают/уменьшают рейтинг статьи/новости на единицу.
    def like(self):
        self.rate += 1
        self.save()

    def dislike(self):
        self.rate -= 1
        self.save()

    def preview(self):
        if len(self.text) > 124:
            return f"{self.text[:124]}..."
        elif len(self.text) == 124:
            return self.text[:124]
        else:
            return self.text

    def __str__(self):
        return f'{self.title}\n{self.add_date.strftime("%d.%m.%Y")}\n{self.text}'

    def get_absolute_url(self):
        return reverse('post', args=[str(self.id)])


# Модель PostCategory
# Промежуточная модель для связи «многие ко многим»:
# связь «один ко многим» с моделью Post;
# связь «один ко многим» с моделью Category.
class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


# Модель Comment
# Под каждой новостью/статьёй можно оставлять комментарии, поэтому необходимо организовать
# их способ хранения тоже.
# Модель будет иметь следующие поля:
# связь «один ко многим» с моделью Post;
# связь «один ко многим» со встроенной моделью User (комментарии может оставить
# любой пользователь, необязательно автор);
# текст комментария;
# дата и время создания комментария;
# рейтинг комментария.
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    add_datetime = models.DateTimeField(auto_now_add=True)
    rate = models.IntegerField(default=0)

    # Методы like() и dislike() увеличивают/уменьшают рейтинг комментария на единицу.
    def like(self):
        self.rate += 1
        self.save()

    def dislike(self):
        self.rate -= 1
        self.save()
