from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.http import HttpRequest
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from apps.extra.models import Document
from apps.trading.models import Trader, Currency, Balance_update
from utils.functions import send_new_password, pin_generator


def sign_in(request: HttpRequest):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            return redirect('main')
        
        else:
            messages.error(request, _("Username or password is invalid"))
            return redirect("sign_in")

    context = {
        '2fauth': Document.objects.filter(document_type='2fauth').first(),
        'privacy_policy': Document.objects.filter(document_type='privacy_policy').first(),
    }

    return render(request, 'authentication/sign_in.html', context=context)


def sign_up(request):

    reff = request.GET.get('reff', '')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        reff = request.POST.get('reff')

        if Trader.objects.filter(username=username).exists():
            messages.error(request, _("This username is already taken"))
            return redirect('sign_up')

        user = Trader(username=username)
        user.set_password(password)
        user.save()

        if user.hash_code != reff:
            reff_user = Trader.objects.filter(hash_code=reff).first()
            if reff_user:
                user.reff_hash_code = reff
                user.save()

                currency = Currency.objects.filter(name='USD').first()

                bonus_balance = Balance_update(
                    trader=reff_user,
                    update_type='plus',
                    currency_type=currency.currency_type,
                    currency=currency,
                    amount=1,
                    confirmed=True,
                    payed=True
                )
                bonus_balance.save()

        login(request, user)
        return redirect('main')

    context = {
        'user_agreement': Document.objects.filter(document_type='user_agreement').first(),
        'privacy_policy': Document.objects.filter(document_type='privacy_policy').first(),
        'reff': reff,
    }

    return render(request, 'authentication/sign_up.html', context=context)


def forgot_password(request):

    if request.POST:
        email = request.POST.get('email')
        trader = Trader.objects.filter(email=email).first()
        if trader:
            new_pass = pin_generator(8)
            send_new_password(new_pass, email)
            trader.set_password(new_pass)
            trader.save()
            messages.success(request, _("New password is sent to your email"))
            return redirect(sign_in)
        else:
            messages.error(request, _("This email has not been registered"))
            return redirect("forgot_password")

    return render(request, 'authentication/forgot_password.html')


def lock(request):

    trader = Trader.objects.filter(pk=request.user.id).first()
    if trader:

        if request.POST:
            password = request.POST.get('password')
            if trader.check_password(password):
                trader.status = 'active'
            else:
                messages.error(request, _("Password is wrong"))
        else:
            trader.status = 'locked'
            
        trader.save()

    return redirect('main')


def sign_out(request):

    logout(request)

    return redirect('sign_in')
