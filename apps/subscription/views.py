from django.shortcuts import render
from apps.trading.models import Currency, Trader
from .models import *


def subscription(request):

    trader = Trader.objects.filter(pk=request.user.id).first()
    if trader:
        current_subscription = trader.current_subscription_type['status']
    else:
        current_subscription = 'simple'

    periods = Subscription_period.objects.all()
    if request.GET.get('period_id'):
        current_period = periods.filter(pk=request.GET.get('period_id')).first()
        if not current_period:
            current_period = periods.first()
    else:
        current_period = periods.first()

    currencies = Currency.objects.filter(status=True)
    if request.GET.get('currency_id'):
        current_currency = currencies.filter(pk=request.GET.get('currency_id')).first()
        if not current_currency:
            current_currency = currencies.first()
    else:
        current_currency = currencies.first()
    
    prices = Subscription_price.objects.filter(subscription_period=current_period, currency=current_currency).order_by('subscription_type')

    context = {
        'periods': periods,
        'current_period': current_period,
        'currencies': currencies,
        'current_currency': current_currency,
        'prices': prices,
        'current_subscription': current_subscription,
    }

    return render(request, 'subscription/subscription.html', context=context)
