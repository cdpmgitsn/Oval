from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from apps.subscription.models import Subscription_update, Subscription
from datetime import date, timedelta
from PIL import Image
import os


class Trader(User):

    subscription_types = (
        ('simple', 'Oval Simple'),
        ('medium', 'Oval Medium'),
        ('pro', 'Oval Pro'),
    )

    themes = (
        ('light', 'light'),
        ('dark', 'dark'),
    )

    status_types = (
        ('active', 'active'),
        ('locked', 'locked'),
    )

    image = models.ImageField("Фотография", upload_to="img/trader", null=True, blank=True)
    date_of_birth = models.DateField("Дата рождения", null=True, blank=True)
    city = models.ForeignKey("location.City", on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField("Адрес", max_length=255, null=True, blank=True)
    email_verified = models.BooleanField("Проверка почты", default=False)
    bot_first_name = models.CharField("Имя", max_length=255, null=True, blank=True)
    bot_last_name = models.CharField("Фамилия", max_length=255, null=True, blank=True)
    bot_username = models.CharField("Имя пользователя", max_length=255, null=True, blank=True)
    bot_user_id = models.BigIntegerField("ID пользователя", null=True, blank=True)
    bot_phone_number = models.CharField("Телефонный номер", max_length=255, null=True, blank=True)
    bot_lang_code = models.CharField("Язык", max_length=255, null=True, blank=True, default='ru')
    bot_registration_finished = models.BooleanField("Завершил регистрацию", default=False)
    hash_code = models.CharField("Хеш", max_length=255, null=True, blank=True)
    reff_hash_code = models.CharField("Хеш", max_length=255, null=True, blank=True)
    choose_currency = models.BooleanField("Выбрал валюту", default=False)
    subscription_type = models.CharField("Тип пользователья", max_length=255, choices=subscription_types, default='simple')
    theme = models.CharField("Тема", max_length=255, choices=themes, default='light')
    status = models.CharField("Статус", max_length=255, choices=status_types, default='active')

    class Meta:
        ordering = ['id',]
        verbose_name = "Трейдер"
        verbose_name_plural = "Трейдеры"

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.username

    @property
    def date_of_birth_format(self):
        if self.date_of_birth:
            return self.date_of_birth.strftime("%d.%m.%Y")

    @property
    def date_joined_format(self):
        if self.date_joined:
            return self.date_joined.strftime("%H:%M:%S %d.%m.%Y")

    @property
    def current_subscription_type(self):
        result = ''
        
        if self.subscription_type == 'pro':
            pro_days = Subscription_update.objects.filter(
                trader=self,
                subscription_type__name='pro',
            ).aggregate(Sum('days'))['days__sum']
            if pro_days == None:
                pro_days = 0

            if pro_days > 0:
                result = 'pro'
            else:
                medium_days = Subscription_update.objects.filter(
                    trader=self,
                    subscription_type__name='medium',
                ).aggregate(Sum('days'))['days__sum']
                if medium_days == None:
                    medium_days = 0

                if medium_days > 0:
                    result = 'medium'
                else:
                    result = 'simple'
        elif self.subscription_type == 'medium':
            medium_days = Subscription_update.objects.filter(
                trader=self,
                subscription_type__name='medium',
            ).aggregate(Sum('days'))['days__sum']
            if medium_days == None:
                medium_days = 0

            if medium_days > 0:
                result = 'medium'
            else:
                result = 'simple'
        else:
            result = 'simple'

        if result in ['pro', 'medium']:
            days = Subscription_update.objects.filter(
                trader=self,
                subscription_type__name=result,
            ).aggregate(Sum('days'))['days__sum']
            if days is None:
                days = 0
            
            total_days = Subscription_update.objects.filter(
                Q(trader=self)
            ).filter(
                Q(subscription_type__name='pro')
                |
                Q(subscription_type__name='medium')
            ).aggregate(Sum('days'))['days__sum']
            if total_days is None:
                total_days = 0
            
            today = date.today()
            next_payment = today + timedelta(days=total_days)
            
            response = {
                'status': result,
                'days': days,
                'total_days': total_days,
                'next_payment': next_payment.strftime("%d.%m.%Y"),
            }
        else:
            response = {
                'status': result,
                'days': 0,
                'total_days': 0,
            }
        
        return response

    def __str__(self) -> str:
        return self.full_name


class Credit_card(models.Model):

    card_types = (
        ('VISA', 'Visa'),
        ('MASTERCARD', 'MasterCard'),
        ('AMEX', 'American Express'),
    )

    trader = models.ForeignKey(Trader, on_delete=models.RESTRICT, verbose_name="Трейдер")
    name = models.CharField(max_length=255, verbose_name='Название')
    number = models.CharField(max_length=255, verbose_name='Номер')
    expiration_date = models.DateField(verbose_name='Дата окончания срока')
    cvv = models.CharField(max_length=4, verbose_name='CVV')
    card_type = models.CharField(max_length=255, verbose_name='Тип карты', choices=card_types, null=True, blank=True)
    verified = models.BooleanField("Verified", default=False)

    class Meta:
        ordering = ['id',]
        verbose_name = 'Кредитная карта'
        verbose_name_plural = 'Кредитные карты'

    @property
    def full_number(self):
        return f"{self.number[0:4]} {self.number[4:8]} {self.number[8:12]} {self.number[12:16]}"

    @property
    def short_number(self):
        return f"**** **** **** {self.number[-4:]}"

    def __str__(self):
        return f"{self.name}'s {self.card_type} ending in {self.expiration_date}"


class Stock_amount(models.Model):

    amount = models.IntegerField("Сумма")

    class Meta:
        ordering = ['amount',]
        verbose_name = "Стоковая сумма"
        verbose_name_plural = "Стоковые суммы"

    def __str__(self) -> str:
        return f"{self.amount}"


class Currency(models.Model):
    
    currency_types = (
        ('fiat', 'Fiat'),
        ('crypto', 'Crypto'),
        ('bonus', 'Bonus'),
    )
    
    currency_type = models.CharField("Тип валюты", max_length=10, choices=currency_types)
    name = models.CharField("Название", max_length=50)
    symbol = models.CharField("Символ", max_length=10)

    stock_amounts = models.ManyToManyField(Stock_amount, blank=True, verbose_name="Стоковые суммы")

    simple = models.BooleanField("Simple", default=False)
    medium = models.BooleanField("Medium", default=False)
    pro = models.BooleanField("Pro", default=True)

    simple_max_price = models.FloatField("Simple max price", default=0)
    medium_max_price = models.FloatField("Medium max price", default=0)
    pro_max_price = models.FloatField("Pro max price", default=0)
    
    country = models.CharField("Страна", max_length=50, null=True, blank=True)
    blockchain = models.CharField("Блокчейн", max_length=50, null=True, blank=True)
    wallet = models.CharField("Кошелёк", max_length=255, null=True, blank=True)
    holder = models.CharField("Держатель", max_length=255, null=True, blank=True)
    status = models.BooleanField("Статус", default=False)

    class Meta:
        ordering = ['id',]
        verbose_name = "Валюта"
        verbose_name_plural = "Валюты"

    def __str__(self):
        if self.currency_type == 'fiat':
            return f"{self.name} {self.symbol} - {self.country}"
        else:
            return f"{self.name} ({self.symbol})"


class Exchange(models.Model):

    exchange_types = (
        ('buy', 'buy'),
        ('sell', 'sell'),
    )

    currency_types = (
        ('fiat', 'fiat'),
        ('crypto', 'crypto'),
    )

    trader = models.ForeignKey(Trader, on_delete=models.CASCADE, verbose_name="Трейдер", null=True, blank=True)
    currency_type = models.CharField("Тип валюты", max_length=255, choices=currency_types, default='fiat')
    exchange_type = models.CharField("Тип обмена", max_length=255, choices=exchange_types, default='buy')
    currency_from = models.ForeignKey(Currency, on_delete=models.RESTRICT, verbose_name="Валюта (из)", related_name="currency_from", null=True, blank=True)
    amount_input = models.FloatField("Количество ввода", default=0)
    currency_to = models.ForeignKey(Currency, on_delete=models.RESTRICT, verbose_name="Валюта (в)", related_name="currency_to", null=True, blank=True)
    amount_output = models.FloatField("Количество выхода", default=0)
    fees = models.FloatField("Комиссия", default=1)
    rate = models.FloatField("Курс", default=0)
    credit_card = models.CharField("Кредитная карта", max_length=255, null=True, blank=True)
    wallet = models.CharField("Кошелёк", max_length=255, null=True, blank=True)
    confirmed = models.BooleanField("Подтверждено", default=False)
    date = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        ordering = ['id',]
        verbose_name = "Обмен"
        verbose_name_plural = "Обмены"

    @property
    def amount_input_format(self):
        return '{:,.0f}'.format(self.amount_input)

    @property
    def amount_output_format(self):
        return '{:,.0f}'.format(self.amount_output)

    @property
    def exchange_currencies(self):
        if self.currency_from and self.currency_to:
            return f"{self.currency_from.currency_type[0]}2{self.currency_to.currency_type[0]}"
        return None

    @property
    def pure_fees(self):
        return self.fees * 100 - 100

    def __str__(self) -> str:
        return f"{self.trader}, {self.amount_input} {self.currency_from} > {self.amount_output} {self.currency_to}"


class Balance_update(models.Model):

    update_types = (
        ('plus', 'plus'),
        ('minus', 'minus'),
    )

    currency_types = (
        ('fiat', 'fiat'),
        ('crypto', 'crypto'),
    )

    payment_types = (
        ('Payme', 'Payme'),
        ('Click', 'Click'),
    )

    def get_bill_path(instance, filename):
        ext = filename.split('.')[-1]
        filename = f"product{instance.date}.{ext}"
        filepath = os.path.join(f"img/balance-bill", filename)
        return filepath

    trader = models.ForeignKey(Trader, on_delete=models.CASCADE, verbose_name="Трейдер", null=True, blank=True)
    update_type = models.CharField("Тип обновления", max_length=255, choices=update_types)
    currency_type = models.CharField("Тип валюты", max_length=255, choices=currency_types, default='fiat')
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT, verbose_name="Валюта", null=True, blank=True)
    amount = models.FloatField("Количество", default=0)
    payment_type = models.CharField("Тип оплаты", max_length=255, choices=payment_types, null=True, blank=True)
    confirmed = models.BooleanField("Подтверждено", default=False)
    payed = models.BooleanField("Оплачено", default=False)
    wallet = models.CharField("Кошелёк", max_length=255, null=True, blank=True)
    bill = models.ImageField("Чек", upload_to=get_bill_path, null=True)
    date = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        ordering = ['id',]
        verbose_name = "Обновление баланса"
        verbose_name_plural = "Обновления балансов"

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        
        if self.bill:
            img = Image.open(self.bill.path)
            real_dimension = img.height + img.width
            if real_dimension > 10000:
                available_dimension = 10000
                diff = real_dimension / available_dimension
                new_width = int(img.width / diff) - 1
                new_height = int(img.height / diff) - 1
                img.thumbnail((new_width, new_height))
                img.save(self.bill.path)
            
            max_size = 5
            image_size = os.path.getsize(self.bill.path) / 1024 / 1024
            if image_size > max_size:
                resize_percent = int((max_size / image_size) * 100)
                img.save(self.bill.path, quality=resize_percent)

    @property
    def amount_format(self):
        return '{:,.0f}'.format(self.amount)

    def __str__(self) -> str:
        if self.currency:
            return f"{self.trader}, {self.amount} {self.currency.name}, {self.update_type}"
        else:
            return f"{self.trader}, {self.amount} {self.currency}, {self.update_type}"


class Withdraw(models.Model):

    currency_types = (
        ('fiat', 'fiat'),
        ('crypto', 'crypto'),
    )

    trader = models.ForeignKey(Trader, on_delete=models.CASCADE, verbose_name="Трейдер", null=True, blank=True)
    currency_type = models.CharField("Тип валюты", max_length=255, choices=currency_types, default='fiat')
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT, verbose_name="Валюта", null=True, blank=True)
    amount = models.FloatField("Количество", default=0)
    fees = models.FloatField("Комиссия", default=1)
    credit_card = models.CharField("Кредитная карта", max_length=255, null=True, blank=True)
    wallet = models.CharField("Кошелёк", max_length=255, null=True, blank=True)
    confirmed = models.BooleanField("Подтверждено", default=False)
    accepted = models.BooleanField("Принято", default=False)
    date = models.DateTimeField("Дата", auto_now_add=True, null=True)

    class Meta:
        ordering = ['id',]
        verbose_name = "Вывод средств"
        verbose_name_plural = "Выводы средств"

    @property
    def amount_format(self):
        return '{:,.0f}'.format(self.amount)

    @property
    def pure_fees(self):
        return self.fees * 100 - 100

    def __str__(self) -> str:
        return f"{self.trader} {self.currency}"


class Send(models.Model):

    currency_types = (
        ('fiat', 'fiat'),
        ('crypto', 'crypto'),
    )

    trader = models.ForeignKey(Trader, on_delete=models.CASCADE, verbose_name="Трейдер", null=True, blank=True ,related_name="trader")
    currency_type = models.CharField("Тип валюты", max_length=255, choices=currency_types, default='fiat')
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT, verbose_name="Валюта", null=True, blank=True)
    amount = models.FloatField("Количество", default=0)
    receiver = models.ForeignKey(Trader, on_delete=models.CASCADE, verbose_name="Получатель", null=True, blank=True ,related_name="receiver")
    confirmed = models.BooleanField("Подтверждено", default=False)
    accepted = models.BooleanField("Принято", default=False)
    denied = models.BooleanField("Отказано", default=False)
    message_id = models.BigIntegerField("ID сообщения", default=0)
    date = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        ordering = ['id',]
        verbose_name = "Отправка"
        verbose_name_plural = "Отправки"

    @property
    def amount_format(self):
        return '{:,.0f}'.format(self.amount)

    @property
    def id_from(self):
        if self.trader:
            return self.trader.bot_user_id

    @property
    def id_to(self):
        if self.receiver:
            return self.receiver.bot_user_id

    @property
    def hash_from(self):
        if self.trader:
            return self.trader.hash_code

    @property
    def hash_to(self):
        if self.receiver:
            return self.receiver.hash_code

    def __str__(self) -> str:
        return f"{self.trader} sent {self.amount} {self.currency} to {self.receiver}"


class Rate_template(models.Model):

    currency_from = models.ForeignKey(Currency, on_delete=models.RESTRICT, verbose_name="Валюта из", related_name="currency_from+")
    currency_to = models.ForeignKey(Currency, on_delete=models.RESTRICT, verbose_name="Валюта в", related_name="currency_to+")
    amount = models.FloatField("Цена", default=1)

    class Meta:
        ordering = ['currency_from', 'currency_to', 'amount']
        verbose_name = "Шаблон валюты"
        verbose_name_plural = "Шаблоны валют"

    @property
    def amount_format(self):
        return f"{self.amount}".replace(',', '.')

    @property
    def display_format(self):
        if self.amount > 1:
            return '{:,.1f}'.format(self.amount)
        else:
            precision = int(str(self.amount).split('-')[1]) + 1
            return "{:.{}f}".format(self.amount, round(precision))

    def __str__(self) -> str:
        return f"{self.currency_from} > {self.amount} {self.currency_to}"
