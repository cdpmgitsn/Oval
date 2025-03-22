from django.db import models


class Subscription_type(models.Model):

    subscription_types = (
        ('simple', 'Oval Simple'),
        ('medium', 'Oval Pro'),
        ('pro', 'Oval Empire'),
    )

    status_types = (
        ('active', 'active'),
        ('deactive', 'deactive'),
    )

    order = models.IntegerField("Очередь", default=0)
    name = models.CharField("Название", max_length=255, choices=subscription_types)
    description = models.TextField("Преимущество подписки (для бота)")
    is_popular = models.BooleanField("Популярный", default=False)
    status = models.CharField("Статус", max_length=255, choices=status_types, default='active')

    class Meta:
        ordering = ['order',]
        verbose_name = "Тип подписки"
        verbose_name_plural = "Типы подписок"

    @property
    def new_name(self):
        values = {
            'simple': 'Simple',
            'medium': 'Pro',
            'pro': 'Empire',
        }
        return values.get(self.name)
    
    @property
    def capital_name(self):
        return self.name.capitalize()

    @property
    def features(self):
        return Subscription_feature.objects.filter(subscription_type=self, status='active')

    # @property
    # def features(self):
    #     array = self.description.split('-')
    #     return array

    def __str__(self) -> str:
        return self.name


class Subscription_feature(models.Model):

    status_types = (
        ('active', 'active'),
        ('deactive', 'deactive'),
    )

    order = models.IntegerField("Очередь", default=0)
    subscription_type = models.ForeignKey(Subscription_type, on_delete=models.RESTRICT, verbose_name="Тип подписки")
    name = models.CharField("Название", max_length=255)
    status = models.CharField("Статус", max_length=255, choices=status_types, default='active')

    class Meta:
        ordering = ['subscription_type', 'order']
        verbose_name = "Преимущество подписки (для сайта)"
        verbose_name_plural = "Преимущества подписок (для сайта)"

    @property
    def bold_name(self):
        array = self.name.split(':')
        if len(array) == 2:
            result = f"{array[0]}:<b>{array[1]}</b>"
        else:
            result = self.name
        return result

    def __str__(self) -> str:
        return self.name


class Subscription_period(models.Model):

    status_types = (
        ('active', 'active'),
        ('deactive', 'deactive'),
    )

    order = models.IntegerField("Очередь", default=0)
    name = models.CharField("Название", max_length=255)
    months = models.IntegerField("Месяца", default=1)
    discount = models.IntegerField("Скидка", default=0)
    status = models.CharField("Статус", max_length=255, choices=status_types, default='active')

    class Meta:
        ordering = ['order',]
        verbose_name = "Периуд подписки"
        verbose_name_plural = "Периуды подписок"

    def __str__(self) -> str:
        return self.name


class Subscription_price(models.Model):

    subscription_type = models.ForeignKey(Subscription_type, on_delete=models.RESTRICT, verbose_name="Тип подписки")
    subscription_period = models.ForeignKey(Subscription_period, on_delete=models.RESTRICT, verbose_name="Периуд подписки")
    currency = models.ForeignKey("trading.Currency", on_delete=models.RESTRICT, verbose_name="Валюта", null=True, blank=True)
    initial_price = models.FloatField("Изначальная цена", default=0)
    price = models.FloatField("Цена", default=0)

    class Meta:
        ordering = ['id',]
        verbose_name = "Цена подписки"
        verbose_name_plural = "Цены подписок"

    @property
    def price_details(self):
        return {
            'currency': self.currency.symbol,
            'integer': int(self.price),
            'decimals': f"{self.price - int(self.price)}"[2:],
        }

    def __str__(self) -> str:
        return f"{self.subscription_type} subscription for {self.subscription_period} is {self.price}"


class Subscription(models.Model):

    payment_types = (
        ('Payme', 'Payme'),
        ('Click', 'Click'),
    )

    trader = models.ForeignKey("trading.Trader", on_delete=models.RESTRICT, verbose_name="Трейдер")
    subscription_type = models.ForeignKey(Subscription_type, on_delete=models.RESTRICT, verbose_name="Тип подписки", null=True, blank=True)
    subscription_period = models.ForeignKey(Subscription_period, on_delete=models.RESTRICT, verbose_name="Периуд подписки", null=True, blank=True)
    currency = models.ForeignKey("trading.Currency", on_delete=models.RESTRICT, verbose_name="Валюта", null=True, blank=True)
    price = models.FloatField("Цена", default=0)
    payment_type = models.CharField("Тип оплаты", max_length=255, choices=payment_types, null=True, blank=True)
    payed = models.BooleanField("Оплачено", default=False)
    date = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        ordering = ['id',]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self) -> str:
        return f"{self.trader} - {self.subscription_type} subscription for {self.subscription_period}"


class Subscription_update(models.Model):

    update_types = (
        ('plus', 'plus'),
        ('minus', 'minus'),
    )

    trader = models.ForeignKey("trading.Trader", on_delete=models.RESTRICT, verbose_name="Трейдер")
    subscription_type = models.ForeignKey(Subscription_type, on_delete=models.RESTRICT, verbose_name="Тип подписки")
    update_type = models.CharField("Тип обновления", max_length=255, choices=update_types)
    days = models.IntegerField("Дни", default=0)
    date = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        ordering = ['id',]
        verbose_name = "Обновление подписки"
        verbose_name_plural = "Обновления подписок"

    def __str__(self) -> str:
        return f"{self.trader}"
