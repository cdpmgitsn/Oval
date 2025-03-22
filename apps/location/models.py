from django.db import models


class Country(models.Model):

    name = models.CharField("Название", max_length=255)
    code = models.CharField("Код", max_length=255)

    class Meta:
        ordering = ['id',]
        verbose_name = "Страна"
        verbose_name_plural = "Страны"

    def __str__(self) -> str:
        return self.name


class City(models.Model):

    country = models.ForeignKey(Country, on_delete=models.RESTRICT, verbose_name="Страна")
    name = models.CharField("Название", max_length=255)
    code = models.CharField("Код", max_length=255)
    use_in_bot = models.BooleanField("Использовать в боте", default=False)

    class Meta:
        ordering = ['id',]
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self) -> str:
        return self.name
