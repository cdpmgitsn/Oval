from rest_framework import serializers
from apps.subscription.models import *
from apps.trading.api.serializers import CurrencySerializer


class Subscription_typeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Subscription_type
        fields = [
            'id',
            'name',
            'description_ru',
            'description_uz',
            'description_en',
            'description_de',
            'description_hi',
        ]


class Subscription_periodSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Subscription_period
        fields = [
            'id',
            'name_ru',
            'name_uz',
            'name_en',
            'name_de',
            'name_hi',
            'months',
            'discount',
        ]


class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):

    subscription_type = Subscription_typeSerializer(read_only=True, many=False)
    subscription_period = Subscription_periodSerializer(read_only=True, many=False)
    currency = CurrencySerializer(read_only=True, many=False)

    class Meta:
        model = Subscription
        fields = ['id', 'subscription_type', 'subscription_period', 'currency', 'price']
