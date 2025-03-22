from django.urls import path
from .views import *

urlpatterns = [
    path('sign_in/', sign_in, name='sign_in'),
    path('sign_up/', sign_up, name='sign_up'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('lock/', lock, name='lock'),
    path('sign_out/', sign_out, name='sign_out'),
]