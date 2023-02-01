from django.contrib import admin
from .models import Author, Category, Post, PostCategory, Comment
# импортируем модель админки для организации перевода моделей
from modeltranslation.admin import TranslationAdmin


# Регистрируем модели для перевода в админке
class CategoryAdminTranslate(TranslationAdmin):
    model = Category


class PostAdminTranslate(TranslationAdmin):
    model = Post


# создаём новый класс для представления товаров в админке
class AuthorAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями,
    # которые вы хотите видеть в таблице с товарами
    list_display = ('author', 'rate')
    list_filter = ('author', 'rate')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)
    list_filter = ('category_name',)


class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'kind', 'add_date', 'title', 'text', 'rate')
    list_filter = ('author', 'kind', 'add_date', 'rate')


class PostCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostCategory._meta.get_fields()]
    list_filter = ('category',)


class CommentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Comment._meta.get_fields()]
    list_filter = ('author', 'add_datetime', 'rate')


# Register your models here.
admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdminTranslate)
# admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdminTranslate)
# admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory, PostCategoryAdmin)
admin.site.register(Comment, CommentAdmin)
