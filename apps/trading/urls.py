from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    path('settings-profile/', login_required(settings_profile), name='settings-profile'),
    path('settings-profile/remove-image/', login_required(remove_image), name='remove-image'),
    path('settings-payment-method/', login_required(settings_payment_method), name='settings-payment-method'),
    path('wallet/', wallet, name='wallet'),
    path('bill/<slug:bill_type>/<pk>/', bill, name='bill'),
    path('rate-templates/', login_required(rate_templates), name='rate-templates'),
]