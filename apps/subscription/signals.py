from django.dispatch import receiver
from django.db.models.signals import pre_save
from .models import *


@receiver(pre_save, sender=Subscription_price)
def set_subscription_price(sender, instance: Subscription_price, **kwargs):
    instance.price = ((100 - instance.subscription_period.discount) / 100) * instance.initial_price * instance.subscription_period.months


@receiver(pre_save, sender=Subscription_update)
def set_subscription_update_amount(sender, instance: Subscription_update, **kwargs):
    if instance.update_type == 'minus' and instance.days > 0:
        instance.amount = instance.days * -1


@receiver(pre_save, sender=Subscription)
def set_subscription_price(sender, instance: Subscription, **kwargs):
    if instance.subscription_type and instance.subscription_period and instance.currency:
        existing_price = Subscription_price.objects.filter(
            subscription_type=instance.subscription_type,
            subscription_period=instance.subscription_period,
            currency=instance.currency,
        ).first()
        if existing_price:
            instance.price = existing_price.price