from django.db import models
from PIL import Image
import os


class About(models.Model):

    name = models.CharField("Название", max_length=255)
    logo = models.ImageField("Логотип", upload_to="img/about/logo")
    profile_icon = models.ImageField("Фотография профиля", upload_to="img/about/profile")
    bot_url = models.URLField("Ссылка бота", null=True, blank=True)

    class Meta:
        ordering = ['id',]
        verbose_name = "О нас"
        verbose_name_plural = "О нас"

    def __str__(self) -> str:
        return self.name


class Tex_work(models.Model):

    status_types = (
        ('active', 'active'),
        ('deactive', 'deactive'),
    )

    order = models.IntegerField("Очередь", default=0)
    name = models.CharField("Название", max_length=255)
    description = models.TextField("Описание")
    poster = models.ImageField("Постер", upload_to="img/tex_work", null=True, blank=True)
    status = models.CharField("Статус", max_length=255, choices=status_types, default='active')

    class Meta:
        ordering = ['order',]
        verbose_name = "Тех работа"
        verbose_name_plural = "Тех работы"

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        
        if self.poster:
            img = Image.open(self.poster.path)
            real_dimension = img.height + img.width
            if real_dimension > 10000:
                available_dimension = 10000
                diff = real_dimension / available_dimension
                new_width = int(img.width / diff) - 1
                new_height = int(img.height / diff) - 1
                img.thumbnail((new_width, new_height))
                img.save(self.poster.path)
            
            max_size = 5
            image_size = os.path.getsize(self.poster.path) / 1024 / 1024
            if image_size > max_size:
                resize_percent = int((max_size / image_size) * 100)
                img.save(self.poster.path, quality=resize_percent)

    def __str__(self) -> str:
        return self.name


class Explanation(models.Model):

    explanation_types = (
        ('hash', 'Мой хеш'),
        ('reff_link', 'Oval partners'),
    )

    status_types = (
        ('active', 'active'),
        ('deactive', 'deactive'),
    )

    explanation_type = models.CharField("Название", max_length=255, choices=explanation_types)
    description = models.TextField("Описание")
    status = models.CharField("Статус", max_length=255, choices=status_types, default='active')

    class Meta:
        ordering = ['id',]
        verbose_name = "Объяснение"
        verbose_name_plural = "Объяснения"

    def __str__(self) -> str:
        return self.explanation_type
