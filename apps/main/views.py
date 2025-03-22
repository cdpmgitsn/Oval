from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from apps.trading.models import *
from apps.notification.models import Notification


def main(request):

    trader = Trader.objects.filter(pk=request.user.id).first()

    if request.POST:
        exchange_id = request.POST.get('exchange_id')
        exchange = Exchange.objects.filter(pk=exchange_id).first()
        if exchange:
            if exchange.trader == trader:
                today = date.today()

                if trader.current_subscription_type['status'] == 'pro':
                    max_exchange_amount = 1000000000000
                elif trader.current_subscription_type['status'] == 'medium':
                    max_exchange_amount = 6
                else:
                    max_exchange_amount = 4
                
                exchanges = Exchange.objects.filter(trader=trader, date__year=today.year, date__month=today.month, confirmed=True).count()
                if not (exchanges < max_exchange_amount):
                    messages.error(request, _("You have exceeded the exchange limit"))
                    return redirect('main')

                exchange.confirmed = True
                exchange.save()

                notification = Notification(
                    _type='exchange',
                    trader=exchange.trader,
                    foreign_object_id=exchange.pk,
                    status='accepted',
                )
                notification.save()

                if exchange.exchange_type == 'buy' and exchange.currency_type == 'fiat':
                    plus_balance = Balance_update(
                        trader=trader,
                        update_type='plus',
                        currency=exchange.currency_from,
                        amount=exchange.amount_input,
                        confirmed=True,
                        payed=True,
                    )
                    plus_balance.save()

                    minus_balance = Balance_update(
                        trader=trader,
                        update_type='minus',
                        currency=exchange.currency_to,
                        amount=exchange.amount_output,
                        confirmed=True,
                        payed=True,
                    )
                    minus_balance.save()
                
                else:
                    plus_balance = Balance_update(
                        trader=trader,
                        update_type='plus',
                        currency=exchange.currency_to,
                        amount=exchange.amount_output,
                        confirmed=True,
                        payed=True,
                    )
                    plus_balance.save()

                    minus_balance = Balance_update(
                        trader=trader,
                        update_type='minus',
                        currency=exchange.currency_from,
                        amount=exchange.amount_input,
                        confirmed=True,
                        payed=True,
                    )
                    minus_balance.save()

                messages.success(request, _("Exchange is confirmed"))
        return redirect('main')

    context = {
        'fiat_currencies': Currency.objects.filter(currency_type='fiat', status=True),
        'crypto_currencies': Currency.objects.filter(currency_type='crypto', status=True),
        'sends': Send.objects.filter(trader=trader),
    }

    return render(request, 'main/main.html', context=context)


def reff_link(request, _hash):

    trader = Trader.objects.filter(pk=request.user.id).first()

    if trader:
        if _hash != trader.hash_code and not trader.reff_hash_code:
            if Trader.objects.filter(hash_code=_hash).exists():
                trader.reff_hash_code = _hash
                trader.save()
        response = redirect('main')
    else:
        response = redirect('sign_up')
        response['location'] += f"?reff={_hash}"
    
    return response


def bank(request):

    context = {
        '': ''
    }

    return render(request, 'main/bank.html', context=context)
