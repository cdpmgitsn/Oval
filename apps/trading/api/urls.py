from django.urls import path
from .views import *

urlpatterns = [
    path('currency/display/', display_currency, name='api-currency-display'),
    path('currency/convert/', convert_currency, name='api-currency-convert'),
    path('currency/view/', CurrencyViewSet.as_view({'get': 'list'}), name='api-currency-view'),
    path('trader/change-currency/', change_currency, name='api-trader-change-currency'),
    path('trader/info/', trader_info, name='api-trader-info'),
    path('trader/check-hash/', trader_check_hash, name='api-trader-check-hash'),
    path('trader/check-username/', check_username, name='api-trader-check-username'),
    path('trader/check-password/', check_password, name='api-trader-check-password'),
    path('trader/create-user/', create_user, name='api-trader-create-user'),
    path('trader/get-lang/', get_lang, name='api-trader-get-lang'),
    path('trader/set-lang/', set_lang, name='api-trader-set-lang'),
    path('trader/logout/', logout_trader, name='api-trader-logout'),
    path('exchange/update/', update_exchange, name='api-exchange-update'),
    path('exchange/rates/', exchange_rates, name='api-exchange-rates'),
    path('exchange/view/', ExchangeViewSet.as_view({'get': 'list'}), name='api-exchange-view'),
    path('balance/update/', update_balance, name='api-balance-update'),
    path('balance/check/', check_balance, name='api-balance-check'),
    path('balance/has/', has_balance, name='api-balance-has'),
    path('balance/get_all/', get_all_balance, name='api-balance-get-all'),
    path('withdraw/update/', update_withdraw, name='api-withdraw-update'),
    path('send/update/', update_send, name='api-send-update'),
]