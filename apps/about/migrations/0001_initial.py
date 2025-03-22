# Generated by Django 4.2.7 on 2023-12-02 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='About',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('logo', models.ImageField(upload_to='img/about/logo', verbose_name='Логотип')),
                ('profile_icon', models.ImageField(upload_to='img/about/profile', verbose_name='Фотография профиля')),
            ],
            options={
                'verbose_name': 'О нас',
                'verbose_name_plural': 'О нас',
                'ordering': ['id'],
            },
        ),
    ]
