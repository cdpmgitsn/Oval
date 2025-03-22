from django.shortcuts import render
from django.db.models import Q, Sum
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.request import Request
from apps.trading.models import *
from apps.notification.models import *
from .serializers import *
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class Subscription_typeViewSet(viewsets.ModelViewSet):

    serializer_class = Subscription_typeSerializer

    def get_queryset(self):

        objs = Subscription_type.objects.all()

        url_data = self.request.GET

        if url_data:
            if 'type' in url_data and url_data['type']:
                if url_data['type'] == 'get_by_id':
                    item_id = url_data['id']
                    objs = objs.filter(id=int(item_id))
                
                elif url_data['type'] == 'get_by_name':
                    name = url_data['name']
                    objs = objs.filter(name=name)
            
            if 'status' in url_data and url_data['status'] in ['active', 'deactive']:
                objs = objs.filter(status=url_data['status'])

        return objs


class Subscription_periodViewSet(viewsets.ModelViewSet):

    serializer_class = Subscription_periodSerializer

    def get_queryset(self):

        objs = Subscription_period.objects.all()

        url_data = self.request.GET

        if url_data:
            if 'type' in url_data and url_data['type']:
                if url_data['type'] == 'get_by_id':
                    item_id = url_data['id']
                    objs = objs.filter(id=int(item_id))

                elif url_data['type'] == 'get_by_name':
                    name = url_data['name']
                    objs = objs.filter(
                        Q(name_ru=name)
                        |
                        Q(name_uz=name)
                        |
                        Q(name_en=name)
                        |
                        Q(name_de=name)
                        |
                        Q(name_hi=name)
                    )

        return objs


@api_view(['POST'])
def update_subscription(request: Request):
    user_id = request.POST.get('user_id')
    if user_id:
        trader = Trader.objects.filter(bot_user_id=int(user_id)).first()
        if trader:
            if request.POST.get('subscription_id'):
                subscription = Subscription.objects.filter(
                    Q(pk=request.POST.get('subscription_id'))
                    &
                    Q(trader=trader)
                ).first()
            else:
                subscription = Subscription.objects.filter(
                    Q(trader=trader)
                    &
                    Q(payed=False)
                ).first()
                if not subscription:
                    subscription = Subscription(trader=trader)

            subscription_type_id = request.POST.get('subscription_type_id')
            if subscription_type_id:
                subscription.subscription_type_id = subscription_type_id

            subscription_period_id = request.POST.get('subscription_period_id')
            if subscription_period_id:
                subscription.subscription_period_id = subscription_period_id

            currency_id = request.POST.get('currency_id')
            if currency_id:
                subscription.currency_id = currency_id

            price = request.POST.get('price')
            if price:
                subscription.price = float(price)

            payment_type = request.POST.get('payment_type')
            if payment_type:
                subscription.payment_type = payment_type

            payed = request.POST.get('payed')
            if payed == 'yes':
                subscription.payed = True

                today = date.today()
                next_date = today + relativedelta(months=subscription.subscription_period.months)
                days = (next_date - today).days
                
                subscription_days = Subscription_update(
                    trader=trader,
                    subscription_type=subscription.subscription_type,
                    update_type='plus',
                    days=days
                )
                subscription_days.save()

                trader.subscription_type = subscription.subscription_type.name
                trader.save()

                notification = Notification(
                    _type='subscription',
                    trader=trader,
                    foreign_object_id=subscription.pk,
                    status='accepted',
                )
                notification.save()

                if trader.reff_hash_code:
                    reff_trader = Trader.objects.filter(hash_code=trader.reff_hash_code).first()
                    if reff_trader:
                        balance_update = Balance_update(
                            trader=reff_trader,
                            update_type='plus',
                            currency_type=subscription.currency.currency_type,
                            currency=subscription.currency,
                            amount=subscription.price * 0.1,
                            confirmed=True,
                            payed=True,
                        )
                        balance_update.save()

            subscription.save()
            return Response({
                'subscription': SubscriptionSerializer(instance=subscription, many=False).data
            }, status=HTTP_200_OK)
        else:
            return Response({'error': 'trader not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'user_id is required field'}, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def subscription_permissions(request: Request):
    user_id = request.POST.get('user_id')
    if user_id:
        trader = Trader.objects.filter(bot_user_id=int(user_id)).first()
        if trader:
            if trader.current_subscription_type['status'] == 'pro':
                max_exchange_amount = 1000000000000
                exchange_fee = 1.00
                max_send_amount = 1000000000000
                max_withdraw_amount = 1000000000000
                withdraw_fee = 1.00
            
            elif trader.current_subscription_type['status'] == 'medium':
                max_exchange_amount = 6
                exchange_fee = 1.01
                max_send_amount = 6
                max_withdraw_amount = 6
                withdraw_fee = 1.01
            
            else:
                max_exchange_amount = 4
                exchange_fee = 1.02
                max_send_amount = 4
                max_withdraw_amount = 4
                withdraw_fee = 1.02
            
            result = {
                'exchange': False,
                'exchange_fee': exchange_fee,
                'send': False,
                'withdraw': False,
                'withdraw_fee': withdraw_fee,
            }
            
            today = date.today()

            exchanges = Exchange.objects.filter(trader=trader, date__year=today.year, date__month=today.month, confirmed=True).count()
            result['exchange'] = exchanges < max_exchange_amount

            sends = Send.objects.filter(trader=trader, date__year=today.year, date__month=today.month, confirmed=True).count()
            result['send'] = sends < max_send_amount

            withdraws = Withdraw.objects.filter(trader=trader, date__year=today.year, date__month=today.month, confirmed=True).count()
            result['withdraw'] = withdraws < max_withdraw_amount
            
            return Response(result, status=HTTP_200_OK)
        else:
            return Response({'error': 'trader not found'}, status=HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'user_id is required field'}, status=HTTP_400_BAD_REQUEST)
