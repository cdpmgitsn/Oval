from django.urls import path
from .views import *

urlpatterns = [
    path('country/view/', CountryViewSet.as_view({'get': 'list'}), name='api-country-view'),
    path('city/view/', CityViewSet.as_view({'get': 'list'}), name='api-city-view'),
]