from rest_framework import serializers
from apps.trading.models import *


class Stock_amountSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Stock_amount
        fields = ['amount',]


class CurrencySerializer(serializers.HyperlinkedModelSerializer):

    stock_amounts = Stock_amountSerializer(read_only=True, many=True)

    class Meta:
        model = Currency
        fields = ['id', 'currency_type', 'name', 'symbol', 'stock_amounts', 'simple_max_price', 'medium_max_price', 'pro_max_price', 'country', 'wallet', 'holder', 'blockchain']


class ExchangeSerializer(serializers.ModelSerializer):

    currency_from = CurrencySerializer(read_only=True, many=False)
    currency_to = CurrencySerializer(read_only=True, many=False)

    class Meta:
        model = Exchange
        fields = ['id', 'currency_type', 'exchange_type', 'currency_from', 'amount_input', 'currency_to', 'amount_output', 'confirmed', 'date']


class Balance_updateSerializer(serializers.ModelSerializer):

    currency = CurrencySerializer(read_only=True, many=False)

    class Meta:
        model = Balance_update
        fields = ['id', 'currency_type', 'currency', 'amount']


class WithdrawSerializer(serializers.ModelSerializer):

    currency = CurrencySerializer(read_only=True, many=False)

    class Meta:
        model = Withdraw
        fields = ['id', 'currency_type', 'currency', 'amount', 'credit_card', 'wallet', 'confirmed']


class SendSerializer(serializers.HyperlinkedModelSerializer):

    currency = CurrencySerializer(read_only=True, many=False)

    class Meta:
        model = Send
        fields = ['id', 'hash_from', 'hash_to', 'id_from', 'id_to', 'currency_type', 'currency', 'amount']
