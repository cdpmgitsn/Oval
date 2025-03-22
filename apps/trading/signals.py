from django.dispatch import receiver
from django.db.models.signals import pre_save
from apps.trading.api.views import get_currency_data, is_scientific_notation, get_crypto_data
from .models import *
from utils.functions import generate_mixed_hash


@receiver(pre_save, sender=Trader)
def set_trader_hash(sender, instance: Trader, **kwargs):
    if not instance.hash_code:
        new_hash = generate_mixed_hash()
        instance.hash_code = new_hash


@receiver(pre_save, sender=Credit_card)
def set_card_name(sender, instance: Credit_card, **kwargs):
    instance.name = instance.name.upper()


@receiver(pre_save, sender=Exchange)
def set_exchange_output(sender, instance: Exchange, **kwargs):
    result = None
    if not instance.rate:
        if instance.exchange_currencies == 'f2f':
            currency_data = get_currency_data(instance.currency_from.name)
            rate = currency_data['conversion_rates'][instance.currency_to.name]
            result = float(instance.amount_input) * rate
        elif instance.exchange_currencies == 'f2c':
            currency_data = get_crypto_data(instance.currency_to.name.lower(), 'USD')
            real_amount = get_currency_data('USD')['conversion_rates'].get(instance.currency_from.name)
            if is_scientific_notation(real_amount):
                real_amount = format(float(real_amount), f".10f")
            real_amount = real_amount * float(instance.amount_input)
            if currency_data != 0:
                result = real_amount / currency_data
        elif instance.exchange_currencies == 'c2f':
            rate = get_crypto_data(instance.currency_from.name.lower(), 'USD')
            real_amount = get_currency_data('USD')['conversion_rates'].get(instance.currency_to.name)
            if is_scientific_notation(real_amount):
                real_amount = format(float(real_amount), f".10f")
            real_amount = real_amount * float(instance.amount_input)
            result = real_amount * rate
    else:
        result = float(instance.amount_input) * float(instance.rate)

    if result:
        if instance.currency_type == 'fiat':
            if instance.exchange_type == 'buy':
                instance.amount_output = result * float(instance.fees)
            else:
                instance.amount_output = result / float(instance.fees)
        else:
            instance.amount_output = result / float(instance.fees)


@receiver(pre_save, sender=Balance_update)
def set_balance_update_amount(sender, instance: Balance_update, **kwargs):
    if instance.update_type == 'minus' and instance.amount > 0:
        instance.amount = instance.amount * -1
    
    if instance.currency:
        instance.currency_type = instance.currency.currency_type
