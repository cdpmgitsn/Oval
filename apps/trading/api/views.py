from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from django.db.models import Q, Sum
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.request import Request
from apps.location.api.serializers import CitySerializer
from .serializers import *
from .pagination import *
import requests
import json
import re
from apps.notification.models import Notification


def is_scientific_notation(value):
    # Define a regular expression pattern for scientific notation
    scientific_notation_pattern = re.compile(r'^[+-]?\d+(\.\d+)?[eE][+-]?\d+$')

    # Check if the value matches the pattern
    return bool(scientific_notation_pattern.match(str(value)))  


def get_currency_data(currency_name):
    try:
        url = f'https://v6.exchangerate-api.com/v6/{settings.EXCHANGERATE_TOKEN}/latest/{currency_name}'
        response = requests.get(url=url)
        json_data = json.loads(response.text)
        return json_data
    except:
        return {'conversion_rates': {}}


def get_crypto_data(crypto_symbol, fiat_currency='usd'):
    try:
        fiat_currency = fiat_currency.lower()
        base_url = 'https://api.coingecko.com/api/v3'
        endpoint = '/simple/price'
        params = {
            'ids': crypto_symbol,
            'vs_currencies': fiat_currency
        }

        response = requests.get(f'{base_url}{endpoint}', params=params)

        if response.status_code == 200:
            data = response.json()
            return data[crypto_symbol][fiat_currency]
        else:
            return 0
    except Exception as e:
        print(e)
        return 0


@api_view(['GET'])
def display_currency(request: Request):

    trader = Trader.objects.filter(pk=request.user.id).first()

    input_value = request.GET.get('input').strip()
    currency_from_value = request.GET.get('currency_from')
    output_value = request.GET.get('output').strip().replace(',', '')
    currency_to_value = request.GET.get('currency_to')

    currency_from = Currency.objects.filter(pk=currency_from_value).first()
    currency_to = Currency.objects.filter(pk=currency_to_value).first()
    if currency_from and currency_to:
        balance = Balance_update.objects.filter(
            trader=trader, currency=currency_from, payed=True
        ).aggregate(Sum('amount'))['amount__sum']
        if balance == None:
            balance = 0
        
        if balance < float(input_value):
            return Response({'error': 'insufficient balance'})

        new_exchange = Exchange(
            currency_type='fiat',
            exchange_type='sell',
            currency_from=currency_from,
            amount_input=float(input_value),
            currency_to=currency_to,
            amount_output=float(output_value),
        )

        if new_exchange.currency_type == 'fiat':
            if new_exchange.exchange_type == 'buy':
                rate = new_exchange.amount_output / new_exchange.fees / new_exchange.amount_input
            else:
                rate = new_exchange.amount_output * new_exchange.fees / new_exchange.amount_input
        else:
            rate = new_exchange.amount_output * new_exchange.fees / new_exchange.amount_input

        new_exchange.rate = rate

        if trader:
            new_exchange.trader = trader
            if trader.current_subscription_type['status'] == 'pro':
                fees = 1
            elif trader.current_subscription_type['status'] == 'pro':
                fees = 1.01
            else:
                fees = 1.02
            
            new_exchange.fees = fees
            new_exchange.amount_input *= fees
        
        new_exchange.save()
        return Response({
            'from_amount': '{:,.1f}'.format(float(input_value)).strip(),
            'from_currency': currency_from.name,
            'to_amount': '{:,.1f}'.format(float(output_value)).strip(),
            'to_currency': currency_to.name,
            'exchange_id': new_exchange.pk,
            'url': reverse('bill', kwargs={'bill_type': 'exchange', 'pk': new_exchange.pk})
        })
    else:
        return Response({'error': 'currency not found'})


@api_view(['GET'])
def convert_currency(request: Request):

    currency_from_id = request.GET.get('currency_from_id')
    amount = request.GET.get('amount').replace(',', '.')
    currency_to_id = request.GET.get('currency_to_id')

    if currency_from_id and amount and currency_to_id:
        currency_from = Currency.objects.filter(pk=currency_from_id).first()
        currency_to = Currency.objects.filter(pk=currency_to_id).first()

        if currency_from and currency_to:
            result = 0
            rate_format = 0

            if currency_from.currency_type == 'fiat' and currency_to.currency_type == 'fiat':
                currency_data = get_currency_data(currency_from.name)
                rate = currency_data['conversion_rates'].get(currency_to.name)
                result = float(amount) * rate
                rate_format = rate

            elif currency_from.currency_type == 'fiat' and currency_to.currency_type == 'crypto':
                currency_data = get_crypto_data(currency_to.name.lower(), 'USD')
                real_amount = get_currency_data('USD')['conversion_rates'].get(currency_from.name)
                if is_scientific_notation(real_amount):
                    real_amount = format(float(real_amount), f".10f")
                real_amount = real_amount * float(amount)
                if currency_data != 0:
                    result = real_amount / currency_data
                    rate_format = currency_data

            elif currency_from.currency_type == 'crypto' and currency_to.currency_type == 'fiat':
                rate = get_crypto_data(currency_from.name.lower(), 'USD')
                real_amount = get_currency_data('USD')['conversion_rates'].get(currency_to.name)
                if is_scientific_notation(real_amount):
                    real_amount = format(float(real_amount), f".10f")
                real_amount = real_amount * float(amount)
                result = real_amount * rate
                rate_format = rate

            show_format = result / float(amount)
            if is_scientific_notation(show_format):
                show_format = format(float(show_format), f".10f")

            if result > 1:
                result = '{:,.1f}'.format(result)

            return Response({
                'amount': result,
                'amount_format': result,
                'comparison': f"1 {currency_from.name} ~ {show_format} {currency_to.name}"
            }, status=HTTP_200_OK)
        else:
            return Response({'error': 'currency_from or currency_to is not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'currency_from_id and amount and currency_to_id are required fields'}, status=HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def change_currency(request: Request):

    trader = Trader.objects.filter(pk=request.user.id).first()
    if trader:
        trader.choose_currency = True
        trader.save()

    return Response({'status': 'ok'}, status=HTTP_200_OK)


class CurrencyViewSet(viewsets.ModelViewSet):

    serializer_class = CurrencySerializer
    pagination_class = CurrencyPagination

    def get_queryset(self):

        objs = Currency.objects.filter(status=True)

        url_data = self.request.GET

        if url_data:
            if 'type' in url_data and url_data['type']:
                if url_data['type'] == 'get_by_id':
                    item_id = url_data['id']
                    objs = objs.filter(id=int(item_id))

                elif url_data['type'] == 'get_by_name':
                    name = url_data['name']
                    objs = objs.filter(name=name)
            
            elif url_data.get('filter_value'):
                filter_value = url_data.get('filter_value')
                user_id = url_data['user_id']
                if user_id:
                    trader = Trader.objects.filter(bot_user_id=int(user_id)).first()
                    if trader:
                        exchange = Exchange.objects.filter(
                            Q(trader=trader)
                            &
                            Q(confirmed=False)
                        ).first()
                        if exchange:
                            if filter_value == 'currency_from':
                                objs = objs.filter(currency_type=exchange.currency_type)
                            elif filter_value == 'currency_to':
                                objs = objs.filter(currency_type='fiat')

            elif url_data.get('currency_type'):
                objs = objs.filter(currency_type=url_data.get('currency_type'))

            if url_data.get('status'):
                if url_data.get('status') == 'simple':
                    objs = objs.filter(simple=True)
                elif url_data.get('status') == 'medium':
                    objs = objs.filter(medium=True)
                elif url_data.get('status') == 'pro':
                    objs = objs.filter(pro=True)
                
        return objs


@api_view(['GET'])
def trader_info(request: Request):
    user_id = request.GET.get('user_id')
    if user_id:
        trader = Trader.objects.filter(bot_user_id=int(user_id)).first()
        if trader:
            result = {
                'id': trader.bot_user_id,
                'username': trader.username,
                'first_name': trader.first_name,
                'last_name': trader.last_name,
                'email': trader.email,
                'hash': trader.hash_code,
                'subscription': trader.current_subscription_type,
                'date_of_birth': trader.date_of_birth_format,
                'date_joined': trader.date_joined_format,
            }
            return Response(result, status=HTTP_200_OK)
        else:
            return Response({'error': 'trader not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'user_id is required field'}, status=HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def trader_check_hash(request: Request):
    _hash = request.GET.get('hash')
    if _hash:
        hash_exists = Trader.objects.filter(hash_code=_hash).exists()
        return Response({'result': hash_exists}, status=HTTP_200_OK)
    else:
        return Response({'error': 'hash is required field'}, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_username(request: Request):
    username = request.POST.get('username')
    user_id = request.POST.get('user_id')
    if username and user_id:
        username_valid = 'yes'
        trader = Trader.objects.filter(username=username).exclude(bot_user_id=int(user_id)).first()
        if trader:
            username_valid = 'no'
        return Response({'username_valid': username_valid}, status=HTTP_200_OK)
    else:
        return Response({'error': 'username and user_id are required'}, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_password(request: Request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if username and password:
        password_valid = 'no'
        trader_id = None
        trader = Trader.objects.filter(username=username).first()
        if trader and trader.check_password(password):
            trader_id = trader.pk
            password_valid = 'yes'
        return Response({'password_valid': password_valid, 'trader_id': trader_id}, status=HTTP_200_OK)
    else:
        return Response({'error': 'username and password are required'}, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_user(request: Request):
    bot_user = None
    user_id = request.POST.get('user_id')
    if user_id:
        
        trader_id = request.POST.get('trader_id')
        if trader_id:
            bot_user = Trader.objects.filter(pk=int(trader_id)).first()
            bot_user.bot_user_id = int(user_id)

        if not bot_user:
            bot_user = Trader.objects.filter(bot_user_id=int(user_id)).first()
            if not bot_user:
                bot_user = Trader(username=user_id, bot_user_id=int(user_id))

        trader_username = request.POST.get('trader_username')
        if trader_username:
            bot_user.username = trader_username

        password = request.POST.get('password')
        if password:
            bot_user.set_password(password)

        username = request.POST.get('username')
        if username:
            bot_user.bot_username = username

        first_name = request.POST.get('first_name')
        if first_name:
            bot_user.bot_first_name = first_name

        last_name = request.POST.get('last_name')
        if last_name:
            bot_user.bot_last_name = last_name

        phone_number = request.POST.get('phone_number')
        if phone_number:
            bot_user.bot_phone_number = phone_number

        lang_code = request.POST.get('lang_code')
        if lang_code:
            bot_user.bot_lang_code = lang_code

        registration_finished = request.POST.get('registration_finished')
        if registration_finished == 'yes':
            bot_user.bot_registration_finished = True

        city_id = request.POST.get('city_id')
        if city_id:
            bot_user.city_id = city_id

        bot_user.save()

        exchange_id = request.POST.get('exchange_id')
        exchange = Exchange.objects.filter(pk=exchange_id).first()
        if exchange and not exchange.trader:
            exchange.trader = bot_user
            exchange.save()

        return Response({
            'status': 'ok',
            'trader': bot_user.username,
            'password': bot_user.password,
            'registration_finished': bot_user.bot_registration_finished,
            'city': CitySerializer(instance=bot_user.city).data
        }, status=HTTP_200_OK)
    else:
        return Response({'error': 'user_id is required'}, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_lang(request: Request):
    user_id = request.POST.get('user_id')
    if user_id:
        bot_user = Trader.objects.filter(bot_user_id=int(user_id)).first()
        if bot_user:
            return Response({'lang': bot_user.bot_lang_code}, status=HTTP_200_OK)
        else:
            return Response({'error': 'user not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'user_id is required'}, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def set_lang(request: Request):
    user_id = request.POST.get('user_id')
    if user_id:
        bot_user = Trader.objects.filter(bot_user_id=int(user_id)).first()
        if bot_user:
            lang = request.POST.get('lang')
            if lang:
                bot_user.lang_code = lang
                bot_user.save()
                return Response({'result': 'lang updateed'}, status=HTTP_200_OK)
            else:
                return Response({'error': 'lang is required'}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'user not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'user_id is required'}, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_trader(request: Request):
    user_id = request.POST.get('user_id')
    if user_id:
        trader = Trader.objects.filter(bot_user_id=int(user_id)).first()
        if trader:
            trader.bot_user_id = 0
            trader.save()
            return Response({'status': 'logged out'}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'trader not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'user_id is required field'}, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def update_exchange(request: Request):
    user_id = request.POST.get('user_id')
    if user_id:
        trader = Trader.objects.filter(bot_user_id=int(user_id)).first()
        if trader:
            exchange = Exchange.objects.filter(
                Q(trader=trader)
                &
                Q(confirmed=False)
            ).first()
            if not exchange:
                exchange = Exchange(trader=trader)
            else:
                if request.POST.get('new') == 'yes':
                    exchange.delete()
                    exchange = Exchange(trader=trader)

            currency_type = request.POST.get('currency_type')
            if currency_type:
                exchange.currency_type = currency_type

            exchange_type = request.POST.get('exchange_type')
            if exchange_type:
                exchange.exchange_type = exchange_type

            currency_from_id = request.POST.get('currency_from_id')
            if currency_from_id:
                if exchange.currency_type == 'fiat':
                    exchange.currency_from_id = currency_from_id
                else:
                    if exchange.exchange_type == 'buy':
                        exchange.currency_to_id = currency_from_id
                    elif exchange.exchange_type == 'sell':
                        exchange.currency_from_id = currency_from_id

            amount_input = request.POST.get('amount_input')
            if amount_input:
                exchange.amount_input = float(amount_input)

            currency_to_id = request.POST.get('currency_to_id')
            if currency_to_id:
                if exchange.currency_type == 'fiat':
                    exchange.currency_to_id = currency_to_id
                else:
                    if exchange.exchange_type == 'buy':
                        exchange.currency_from_id = currency_to_id
                    elif exchange.exchange_type == 'sell':
                        exchange.currency_to_id = currency_to_id

            credit_card = request.POST.get('credit_card')
            if credit_card:
                exchange.credit_card = credit_card.upper()

            wallet = request.POST.get('wallet')
            if wallet:
                exchange.wallet = wallet

            rate = request.POST.get('rate')
            if rate:
                exchange.rate = rate

            fees = request.POST.get('fees')
            if fees:
                exchange.fees = fees

            amount_output = request.POST.get('amount_output')
            if amount_output:
                exchange.amount_output = float(amount_output)

            confirmed = request.POST.get('confirmed')
            if confirmed == 'yes':
                exchange.confirmed = True
                
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
            
            exchange.save()
            return Response({
                'exchange': ExchangeSerializer(instance=exchange, many=False).data
            }, status=HTTP_200_OK)
        else:
            return Response({'error': 'trader not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'user_id is required field'}, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def exchange_rates(request: Request):
    exchange_id = request.POST.get('exchange_id')
    if exchange_id:
        exchange = Exchange.objects.filter(pk=exchange_id).first()
        if exchange:
            result = []

            if exchange.currency_type == 'fiat':
                if exchange.exchange_type == 'buy':
                    output_value = exchange.amount_output / exchange.fees / exchange.amount_input
                else:
                    output_value = exchange.amount_output * exchange.fees / exchange.amount_input
            else:
                output_value = exchange.amount_output * exchange.fees / exchange.amount_input

            if output_value > 1:
                output_value = '{:,.1f}'.format(output_value)
            else:
                precision = int(str(output_value).split('-')[1]) + 1
                output_value = "{:.{}f}".format(output_value, round(precision))
            
            initial_rate = f"1 {exchange.currency_from.name} = {output_value} {exchange.currency_to.name}"
            result.append({
                'type': 'initial',
                'rate': initial_rate,
                'slug_value': f'{output_value}'.replace(',', '')
            })
            templates = Rate_template.objects.filter(currency_from=exchange.currency_from, currency_to=exchange.currency_to)
            for item in templates:
                result.append({
                    'type': 'template',
                    'template_id': item.pk,
                    'rate': f"1 {item.currency_from.name} = {item.display_format} {item.currency_to.name}",
                    'slug_value': f'{item.display_format}'.replace(',', '')
                })
            return Response({'status': 'ok', 'rates': result})
        else:
            return Response({'error': 'exchange not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'exchange_id is required'}, status=HTTP_400_BAD_REQUEST)


class ExchangeViewSet(viewsets.ModelViewSet):

    serializer_class = ExchangeSerializer

    def get_queryset(self):

        objs = Exchange.objects.all()

        url_data = self.request.GET

        if url_data:
            if 'type' in url_data and url_data['type']:
                if url_data['type'] == 'get_by_id':
                    item_id = url_data['id']
                    objs = objs.filter(id=int(item_id))
                
                elif url_data['type'] == 'get_by_user_id':
                    user_id = url_data['user_id']
                    objs = objs.filter(trader__bot_user_id=int(user_id))
                    if url_data.get('currency_type') in ['fiat', 'crypto']:
                        objs = objs.filter(currency_from__currency_type=url_data.get('currency_type'))

        return objs


@api_view(['POST'])
def update_balance(request: Request):
    user_id = request.POST.get('user_id')
    if user_id:
        trader = Trader.objects.filter(bot_user_id=int(user_id)).first()
        if trader:
            if request.POST.get('balance_id'):
                balance = Balance_update.objects.filter(
                    Q(pk=request.POST.get('balance_id'))
                    &
                    Q(trader=trader)
                ).first()
            else:
                balance = Balance_update.objects.filter(
                    Q(trader=trader)
                    &
                    Q(confirmed=False)
                ).first()
                if not balance:
                    balance = Balance_update(trader=trader)

            update_type = request.POST.get('update_type')
            if update_type:
                balance.update_type = update_type

            currency_type = request.POST.get('currency_type')
            if currency_type:
                balance.currency_type = currency_type

            currency_id = request.POST.get('currency_id')
            if currency_id:
                balance.currency_id = currency_id

            amount = request.POST.get('amount')
            if amount:
                balance.amount = float(amount)

            payment_type = request.POST.get('payment_type')
            if payment_type:
                balance.payment_type = payment_type

            confirmed = request.POST.get('confirmed')
            if confirmed == 'yes':
                balance.confirmed = True
            
                notification = Notification(
                    _type='balance_update',
                    trader=balance.trader,
                    foreign_object_id=balance.pk,
                    status='pending',
                )
                notification.save()

            payed = request.POST.get('payed')
            if payed == 'yes':
                balance.payed = True

                notification = Notification.objects.filter(
                    Q(_type='balance_update')
                    &
                    Q(trader=balance.trader)
                    &
                    Q(foreign_object_id=balance.pk)
                ).first()
                if notification:
                    notification.status = 'accepted'
                    notification.save()
                else:
                    notification = Notification(
                        _type='balance_update',
                        trader=balance.trader,
                        foreign_object_id=balance.pk,
                        status='accepted',
                    )
                    notification.save()
                
                bonus_currency = Currency.objects.filter(currency_type='bonus').first()
                if not bonus_currency:
                    bonus_currency = Currency(
                        currency_type='bonus',
                        name='Oval bonus',
                        symbol='.',
                        status=True
                    )
                    bonus_currency.save()
                
                if trader.reff_hash_code:
                    reff_trader = Trader.objects.filter(hash_code=trader.reff_hash_code).first()
                    if reff_trader:
                        balance_update = Balance_update(
                            trader=reff_trader,
                            update_type='plus',
                            currency_type=bonus_currency.currency_type,
                            currency=bonus_currency,
                            amount=5,
                            confirmed=True,
                            payed=True,
                        )
                        balance_update.save()

            balance.save()
            return Response({
                'balance': Balance_updateSerializer(instance=balance, many=False).data
            }, status=HTTP_200_OK)
        else:
            return Response({'error': 'trader not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'user_id is required field'}, status=HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def check_balance(request: Request):
    user_id = request.GET.get('user_id')
    if user_id:
        trader = Trader.objects.filter(bot_user_id=int(user_id)).first()
        if trader:
            currency_id = request.GET.get('currency_id')
            if currency_id:
                currency = Currency.objects.filter(pk=currency_id).first()
            else:
                if request.GET.get('type') == 'bonus':
                    currency = Currency.objects.filter(currency_type='bonus').first()
                elif request.GET.get('type') == 'withdraw':
                    withdraw = Withdraw.objects.filter(
                        Q(trader=trader)
                        &
                        Q(confirmed=False)
                    ).first()
                    if withdraw:
                        currency = withdraw.currency
                    else:
                        return Response({'error': 'trader has no withdraw'}, status=HTTP_400_BAD_REQUEST)
                elif request.GET.get('type') == 'send':
                    send = Send.objects.filter(
                        Q(trader=trader)
                        &
                        Q(confirmed=False)
                    ).first()
                    if send:
                        currency = send.currency
                    else:
                        return Response({'error': 'trader has no send'}, status=HTTP_400_BAD_REQUEST)
                else:
                    exchange = Exchange.objects.filter(
                        Q(trader=trader)
                        &
                        Q(confirmed=False)
                    ).first()
                    if exchange:
                        if exchange.exchange_type == 'buy' and exchange.currency_type == 'fiat':
                            currency = exchange.currency_to
                        else:
                            currency = exchange.currency_from
                    else:
                        return Response({'error': 'trader has no exchange'}, status=HTTP_400_BAD_REQUEST)
            print(currency)
            if currency:
                balance = Balance_update.objects.filter(
                    trader=trader, currency=currency, payed=True
                ).aggregate(Sum('amount'))['amount__sum']
                if balance == None:
                    balance = 0
                return Response({'balance': balance}, status=HTTP_200_OK)
            else:
                return Response({'error': 'currency not found'}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'trader not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'user_id is required'}, status=HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def has_balance(request: Request):
    user_id = request.GET.get('user_id')
    if user_id:
        trader = Trader.objects.filter(bot_user_id=int(user_id)).first()
        if trader:
            result = 'no'
            balance = Balance_update.objects.filter(trader=trader, payed=True).first()
            if balance:
                result = 'yes'
            return Response({'result': result}, status=HTTP_200_OK)
        else:
            return Response({'error': 'trader not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'user_id is required'}, status=HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_balance(request: Request):
    user_id = request.GET.get('user_id')
    if user_id:
        trader = Trader.objects.filter(bot_user_id=int(user_id)).first()
        if trader:
            currencies = Currency.objects.filter(status=True)
            if request.GET.get('currency_type') in ['fiat', 'crypto']:
                currencies = currencies.filter(currency_type=request.GET.get('currency_type'))
            balances = [
                {
                    'currency': item.name,
                    'balance': Balance_update.objects.filter(
                        trader=trader, currency=item, payed=True
                    ).aggregate(Sum('amount'))['amount__sum'],
                    'symbol': item.symbol,
                }
                for item in currencies
            ]
            return Response({'balances': balances}, status=HTTP_200_OK)
        else:
            return Response({'error': 'trader not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'user_id is required'}, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def update_withdraw(request: Request):
    user_id = request.POST.get('user_id')
    if user_id:
        trader = Trader.objects.filter(bot_user_id=int(user_id)).first()
        if trader:
            if request.POST.get('withdraw_id'):
                withdraw = Withdraw.objects.filter(
                    Q(pk=request.POST.get('withdraw_id'))
                    &
                    Q(trader=trader)
                ).first()
            else:
                withdraw = Withdraw.objects.filter(
                    Q(trader=trader)
                    &
                    Q(confirmed=False)
                ).first()

            if not withdraw:
                withdraw = Withdraw(trader=trader)

            currency_type = request.POST.get('currency_type')
            if currency_type:
                withdraw.currency_type = currency_type

            currency_id = request.POST.get('currency_id')
            if currency_id:
                withdraw.currency_id = currency_id

            amount = request.POST.get('amount')
            if amount:
                withdraw.amount = float(amount)

            fees = request.POST.get('fees')
            if fees:
                withdraw.fees = fees

            credit_card = request.POST.get('credit_card')
            if credit_card:
                withdraw.credit_card = credit_card.upper()

            wallet = request.POST.get('wallet')
            if wallet:
                withdraw.wallet = wallet

            confirmed = request.POST.get('confirmed')
            if confirmed == 'yes':
                withdraw.confirmed = True

                notification = Notification(
                    _type='withdraw',
                    trader=withdraw.trader,
                    foreign_object_id=withdraw.pk,
                    status='pending',
                )
                notification.save()
            
            accepted = request.POST.get('accepted')
            if accepted == 'yes':
                if withdraw.accepted != True:
                    new_balance = Balance_update(
                        trader=trader,
                        update_type='minus',
                        currency=withdraw.currency,
                        amount=withdraw.amount,
                        confirmed=True,
                        payed=True,
                    )
                    new_balance.save()

                    notification = Notification.objects.filter(
                        Q(_type='withdraw')
                        &
                        Q(trader=withdraw.trader)
                        &
                        Q(foreign_object_id=withdraw.pk)
                    ).first()
                    if notification:
                        notification.status = 'accepted'
                        notification.save()
                    else:
                        notification = Notification(
                            _type='withdraw',
                            trader=withdraw.trader,
                            foreign_object_id=withdraw.pk,
                            status='accepted',
                        )
                        notification.save()
                withdraw.accepted = True

            withdraw.save()
            return Response({
                'withdraw': WithdrawSerializer(instance=withdraw, many=False).data
            }, status=HTTP_200_OK)
        else:
            return Response({'error': 'trader not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'user_id is required field'}, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def update_send(request: Request):
    user_id = request.POST.get('user_id')
    if user_id:
        trader = Trader.objects.filter(bot_user_id=int(user_id)).first()
        if trader:
            if request.POST.get('send_id'):
                send = Send.objects.filter(
                    Q(pk=request.POST.get('send_id'))
                    &
                    Q(trader=trader)
                ).first()
            else:
                send = Send.objects.filter(
                    Q(trader=trader)
                    &
                    Q(confirmed=False)
                ).first()

            if not send:
                send = Send(trader=trader)

            currency_type = request.POST.get('currency_type')
            if currency_type:
                send.currency_type = currency_type

            currency_id = request.POST.get('currency_id')
            if currency_id:
                send.currency_id = currency_id

            amount = request.POST.get('amount')
            if amount:
                send.amount = float(amount)

            hash_code = request.POST.get('hash_code')
            if hash_code:
                receiver = Trader.objects.filter(hash_code=hash_code).first()
                if receiver:
                    send.receiver = receiver

            confirmed = request.POST.get('confirmed')
            if confirmed == 'yes':
                send.confirmed = True
            
                notification = Notification(
                    _type='send_sender',
                    trader=send.trader,
                    foreign_object_id=send.pk,
                    status='pending',
                )
                notification.save()

                notification = Notification(
                    _type='send_receiver',
                    trader=send.receiver,
                    foreign_object_id=send.pk,
                    status='pending',
                )
                notification.save()

            accepted = request.POST.get('accepted')
            if accepted == 'yes':
                balance = Balance_update.objects.filter(
                    trader=trader, currency=send.currency, payed=True
                ).aggregate(Sum('amount'))['amount__sum']
                if not balance:
                    balance = 0
                
                if balance < send.amount:
                    return Response({'error': 'balance'})

                send.accepted = True

                plus_balance = Balance_update(
                    trader=send.receiver,
                    update_type='plus',
                    currency=send.currency,
                    amount=send.amount,
                    confirmed=True,
                    payed=True,
                )
                plus_balance.save()
                
                minus_balance = Balance_update(
                    trader=send.trader,
                    update_type='minus',
                    currency=send.currency,
                    amount=send.amount,
                    confirmed=True,
                    payed=True,
                )
                minus_balance.save()

                notification = Notification.objects.filter(
                    Q(_type='send_sender')
                    &
                    Q(trader=send.trader)
                    &
                    Q(foreign_object_id=send.pk)
                ).first()
                if notification:
                    notification.status = 'accepted'
                    notification.save()
                else:
                    notification = Notification(
                        _type='send_sender',
                        trader=send.trader,
                        foreign_object_id=send.pk,
                        status='accepted',
                    )
                    notification.save()

                notification = Notification.objects.filter(
                    Q(_type='send_receiver')
                    &
                    Q(trader=send.receiver)
                    &
                    Q(foreign_object_id=send.pk)
                ).first()
                if notification:
                    notification.status = 'accepted'
                    notification.save()
                else:
                    notification = Notification(
                        _type='send_receiver',
                        trader=send.receiver,
                        foreign_object_id=send.pk,
                        status='accepted',
                    )
                    notification.save()

            elif accepted == 'no':
                
                send.denied = True

                notification = Notification.objects.filter(
                    Q(_type='send_sender')
                    &
                    Q(trader=send.trader)
                    &
                    Q(foreign_object_id=send.pk)
                ).first()
                if notification:
                    notification.status = 'denied'
                    notification.save()
                else:
                    notification = Notification(
                        _type='send_sender',
                        trader=send.trader,
                        foreign_object_id=send.pk,
                        status='denied',
                    )
                    notification.save()

                notification = Notification.objects.filter(
                    Q(_type='send_receiver')
                    &
                    Q(trader=send.receiver)
                    &
                    Q(foreign_object_id=send.pk)
                ).first()
                if notification:
                    notification.status = 'denied'
                    notification.save()
                else:
                    notification = Notification(
                        _type='send_receiver',
                        trader=send.receiver,
                        foreign_object_id=send.pk,
                        status='denied',
                    )
                    notification.save()

            message_id = request.POST.get('message_id')
            if message_id:
                send.message_id = int(message_id)

            send.save()
            return Response({
                'send': SendSerializer(instance=send, many=False).data
            }, status=HTTP_200_OK)
        else:
            return Response({'error': 'trader not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'user_id is required field'}, status=HTTP_400_BAD_REQUEST)
