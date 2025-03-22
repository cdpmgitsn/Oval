from django.urls import path
from .views import *

urlpatterns = [
    path('subscription_type/view/', Subscription_typeViewSet.as_view({'get': 'list'}), name='api-subscription_type-view'),
    path('subscription_period/view/', Subscription_periodViewSet.as_view({'get': 'list'}), name='api-subscription_period-view'),
    path('subscription/update/', update_subscription, name='api-subscription-update'),
    path('subscription/permissions/', subscription_permissions, name='api-subscription-permissions'),
]