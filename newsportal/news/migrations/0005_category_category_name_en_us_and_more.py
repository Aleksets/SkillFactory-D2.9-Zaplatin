# Generated by Django 4.1.3 on 2023-01-29 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_alter_category_subscribers'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='category_name_en_us',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='category',
            name='category_name_ru',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='post',
            name='author_en_us',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='news.author'),
        ),
        migrations.AddField(
            model_name='post',
            name='author_ru',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='news.author'),
        ),
        migrations.AddField(
            model_name='post',
            name='kind_en_us',
            field=models.CharField(choices=[('AR', 'Article'), ('NE', 'News')], max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='kind_ru',
            field=models.CharField(choices=[('AR', 'Article'), ('NE', 'News')], max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='text_en_us',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='text_ru',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='title_en_us',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='title_ru',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='kind',
            field=models.CharField(choices=[('AR', 'Article'), ('NE', 'News')], max_length=2),
        ),
    ]
