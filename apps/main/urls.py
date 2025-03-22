from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    path('', main, name='main'),
    path('reff_link/<slug:_hash>/', reff_link, name='reff_link'),
    path('bank/', login_required(bank), name='bank'),
]