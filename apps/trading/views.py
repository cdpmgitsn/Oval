from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.validators import validate_image_file_extension
from django.core.files.storage import default_storage
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from datetime import date
from apps.location.models import *
from apps.notification.models import Notification
from .models import *
from utils.functions import are_decimal_digits_zero
from utils.bot.btns import *
from utils.bot.messages import *
from telebot import TeleBot


def settings_profile(request):

    trader = Trader.objects.filter(pk=request.user.id).first()
    if not trader:
        return redirect('main')

    if request.POST:

        if request.POST.get('type') == 'user-profile':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            username = request.POST['username']
            old_password = request.POST['old_password']
            new_password = request.POST['new_password']
            new_password_again = request.POST['new_password_again']

            trader.first_name = first_name
            trader.last_name = last_name

            if not User.objects.filter(username=username).exclude(pk=trader.pk).exists():
                trader.username = username
            else:
                messages.error(request, _("This username is already taken"))

            if old_password or new_password or new_password_again:
                if old_password and new_password and new_password_again:
                    if trader.check_password(old_password):
                        if new_password == new_password_again:
                            trader.set_password(new_password)
                        else:
                            messages.error(request, _(
                                "New passwords are not the same"))
                    else:
                        messages.error(request, _("Your old password is wrong"))
                else:
                    messages.error(request, _(
                        "In order to change password you have to fill all password fields"))

            messages.success(request, _("Profile successfully edited"))
            trader.save()

        elif request.POST.get('type') == 'user-media':
            image = request.FILES.get('image')
            if image:
                try:
                    # Check image extension
                    validate_image_file_extension(image)

                    # Check image size (20MB limit)
                    max_size = 20 * 1024 * 1024  # 20MB in bytes
                    if image.size > max_size:
                        messages.error(request, _(
                            "Image size exceeds the maximum allowed (20MB)."))
                    else:
                        # Delete old image
                        if trader.image:
                            default_storage.delete(trader.image.name)

                        # Save the new image
                        trader.image = image
                        trader.save()
                        messages.success(request, _(
                            "Profile successfully edited"))
                except:
                    messages.error(request, _(
                        "Invalid image file. Please upload a valid image."))

        elif request.POST.get('type') == 'user-information':
            city_id = request.POST['city_id']
            address = request.POST['address']
            email = request.POST['email']
            date_of_birth = request.POST['date_of_birth']

            trader.city_id = city_id
            trader.address = address
            
            if email:
                if not User.objects.filter(email=email).exclude(pk=trader.pk).exists():
                    trader.email = email
                else:
                    messages.error(request, _("This email is already taken"))
            else:
                trader.email = ''
            
            if date_of_birth:
                trader.date_of_birth = date_of_birth
            else:
                trader.date_of_birth = None

            trader.save()

        return redirect('settings-profile')

    context = {
        'settings_page': 'profile',
        'countries': Country.objects.all()
    }

    return render(request, 'trading/settings-profile.html', context=context)


def remove_image(request):

    trader = Trader.objects.filter(pk=request.user.id).first()
    if not trader:
        return redirect('main')

    if trader.image:
        default_storage.delete(trader.image.name)
        trader.image = None
    trader.save()

    return redirect('settings-profile')


def settings_payment_method(request):

    trader = Trader.objects.filter(pk=request.user.id).first()
    if not trader:
        return redirect('main')

    card_limit = {
        'simple': 2,
        'medium': 3,
        'pro': 1000,
    }

    if request.POST:
        if request.POST.get('type') == 'create':
            if Credit_card.objects.filter(trader=trader).count() < card_limit.get(trader.current_subscription_type['status']):
                name = request.POST.get('name')
                number = request.POST.get('number').replace(' ', '')
                expiration_date = request.POST.get('expiration_date')
                cvv = request.POST.get('cvv')

                new_card = Credit_card(
                    trader=trader,
                    name=name,
                    number=number,
                    expiration_date=date(
                        year=int(expiration_date.split('/')[1]),
                        month=int(expiration_date.split('/')[0]),
                        day=1
                    ),
                    cvv=cvv,
                )
                new_card.save()

                messages.success(request, _("Card successfully created"))
            else:
                messages.error(request, _("Your maximum limit for adding cards is reached"))
        
        elif request.POST.get('type') == 'delete':
            card_id = request.POST.get('card_id')
            card = Credit_card.objects.filter(trader=trader, pk=card_id).first()
            if card:
                card.delete()

            messages.success(request, _("Card successfully deleted"))

        return redirect('settings-payment-method')

    context = {
        'settings_page': 'payment'
    }

    return render(request, 'trading/settings-payment-method.html', context=context)


def wallet(request):

    trader = Trader.objects.filter(pk=request.user.id).first()

    currencies = Currency.objects.filter(status=True)
    if request.GET.get('currency_type') in ['fiat', 'crypto']:
        currencies = currencies.filter(currency_type=request.GET.get('currency_type'))
    
    if request.POST:

        if trader:
            if request.POST.get('type') == 'top_up_balance':
                currency_id = request.POST.get('currency_id')
                amount = request.POST.get('amount')
                wallet = request.POST.get('wallet', '')
                bill_image = request.FILES.get('bill')

                currency = currencies.filter(pk=currency_id).first()
                if currency:
                    balance_update = Balance_update(
                        trader=trader,
                        update_type='plus',
                        currency_type=currency.currency_type,
                        currency=currency,
                        amount=float(amount),
                        confirmed=True,
                        wallet=wallet,
                        bill=bill_image,
                    )
                    balance_update.save()

                    notification = Notification(
                        _type='balance_update',
                        trader=trader,
                        foreign_object_id=balance_update.pk,
                        status='pending',
                    )
                    notification.save()

                    # try:
                    bot = TeleBot(settings.BOT_TOKEN)
                    photo = open(f"{settings.BASE_DIR}/{balance_update.bill.url}", 'rb')
                    msg = f"#️⃣ Номер заявки: {balance_update.pk}\n"
                    msg += f"📎 ID пользователья: {trader.bot_user_id}\n"
                    msg += f"💵 Валюта пополнения: {balance_update.currency.name}\n"
                    msg += f"🔢 Сумма пополнения: {balance_update.amount} {balance_update.currency.name}\n"
                    keyb = accept_balance_btns(trader.bot_lang_code, user_id=trader.bot_user_id, balance_id=balance_update.pk)
                    bot.send_photo(settings.BALANCE_GROUP_ID[balance_update.currency_type], photo, msg, reply_markup=keyb)
                    # except:
                    #     pass
                else:
                    messages.error(request, _("Currency not found"))

            elif request.POST.get('type') == 'withdraw':
                currency_id = request.POST.get('currency_id')
                amount = request.POST.get('amount')
                wallet = request.POST.get('wallet', '')
                credit_card = request.POST.get('credit_card', '')

                currency = currencies.filter(pk=currency_id).first()
                if currency:
                    balance = Balance_update.objects.filter(
                        trader=trader, currency=currency, payed=True
                    ).aggregate(Sum('amount'))['amount__sum']
                    if not balance:
                        balance = 0
                    if float(amount) < balance:
                        if trader.current_subscription_type['status'] == 'pro':
                            fees = 1.00
                        elif trader.current_subscription_type['status'] == 'medium':
                            fees = 1.01                    
                        else:
                            fees = 1.02

                        today = date.today()
                    
                        if trader.current_subscription_type['status'] == 'pro':
                            max_withdraw_amount = 1000000000000
                        elif trader.current_subscription_type['status'] == 'medium':
                            max_withdraw_amount = 6
                        else:
                            max_withdraw_amount = 4
                        
                        withdraws = Withdraw.objects.filter(trader=trader, date__year=today.year, date__month=today.month, confirmed=True).count()
                        if not (withdraws < max_withdraw_amount):
                            messages.error(request, _("You have exceeded the withdrawal limit"))
                            return redirect('main')

                        withdraw = Withdraw(
                            trader=trader,
                            currency_type=currency.currency_type,
                            currency=currency,
                            amount=float(amount),
                            fees=fees,
                            credit_card=credit_card,
                            wallet=wallet,
                            confirmed=True,
                        )
                        withdraw.save()

                        notification = Notification(
                            _type='withdraw',
                            trader=trader,
                            foreign_object_id=withdraw.pk,
                            status='pending',
                        )
                        notification.save()

                        messages.success(request, _("Withdraw is send to our managers"))

                        try:
                            bot = TeleBot(settings.BOT_TOKEN)
                            msg = f"#️⃣ Номер заявки: {withdraw.pk}\n"
                            msg += f"📎 ID пользователья: {trader.bot_user_id}\n"
                            msg += f"💵 Валюта обмена: {withdraw.currency.name}\n"
                            msg += f"🔢 Сумма обмена: {withdraw.amount}\n"
                            if withdraw.credit_card:
                                msg += f"💳 Карта пополнения: {withdraw.credit_card}\n"
                            elif withdraw.wallet:
                                msg += f"💳 Кошелёк пополнения: {withdraw.wallet}\n"
                            keyb = accept_withdraw_btns(trader.bot_lang_code, user_id=trader.bot_user_id, withdraw_id=withdraw.pk)
                            bot.send_message(settings.WITHDRAW_GROUP_ID[withdraw.currency_type], msg, reply_markup=keyb)
                        except:
                            pass
                    else:
                        messages.error(request, _("Insufficient funds in your balance to perform this operation ‼️"))
                else:
                    messages.error(request, _("Currency not found"))

            elif request.POST.get('type') == 'send':
                currency_id = request.POST.get('currency_id')
                amount = request.POST.get('amount')
                _hash = request.POST.get('hash', '')

                currency = currencies.filter(pk=currency_id).first()
                if currency:
                    balance = Balance_update.objects.filter(
                        trader=trader, currency=currency, payed=True
                    ).aggregate(Sum('amount'))['amount__sum']
                    if not balance:
                        balance = 0
                    if float(amount) < balance:

                        receiver = Trader.objects.filter(hash_code=_hash).first()
                        if receiver:
                            today = date.today()
                    
                            if trader.current_subscription_type['status'] == 'pro':
                                max_send_amount = 1000000000000
                            elif trader.current_subscription_type['status'] == 'medium':
                                max_send_amount = 6
                            else:
                                max_send_amount = 4
                            
                            sends = Send.objects.filter(trader=trader, date__year=today.year, date__month=today.month, confirmed=True).count()
                            if not (sends < max_send_amount):
                                messages.error(request, _("You have exceeded the sending limit"))
                                return redirect('main')

                            send = Send(
                                trader=trader,
                                currency_type=currency.currency_type,
                                currency=currency,
                                amount=float(amount),
                                receiver=receiver,
                                confirmed=True,
                            )
                            send.save()

                            notification = Notification(
                                _type='send_sender',
                                trader=trader,
                                foreign_object_id=send.pk,
                                status='pending',
                            )
                            notification.save()

                            notification = Notification(
                                _type='send_receiver',
                                trader=receiver,
                                foreign_object_id=send.pk,
                                status='pending',
                            )
                            notification.save()

                            messages.success(request, _("You successfully send money!"))

                            current_domain = request.META['HTTP_HOST']
                            current_url = request.scheme + '://' + current_domain

                            try:
                                bot = TeleBot(settings.BOT_TOKEN)
                                msg = send_bill_msg.get(trader.bot_lang_code)
                                msg = f'<a href="{current_url}/bill/send/{send.pk}/?viewer=receiver">{msg}</a>'
                                keyb = accept_send_btns(trader.bot_lang_code, trader.bot_user_id, send.pk)
                                message = bot.send_message(send.receiver.bot_user_id, msg, reply_markup=keyb, parse_mode='html')
                                send.message_id = message.message_id
                                send.save()
                            except:
                                pass
                        else:
                            messages.error(request, _("Hash not found"))
                    else:
                        messages.error(request, _("Insufficient funds in your balance to perform this operation ‼️"))
                else:
                    messages.error(request, _("Currency not found"))
            
        return redirect('wallet')

    balances = []
    for item in currencies:
        if trader:
            balance = Balance_update.objects.filter(
                trader=trader, currency=item, payed=True
            ).aggregate(Sum('amount'))['amount__sum']
            if balance:
                if balance > 1:
                    if are_decimal_digits_zero(balance):
                        balance = '{:7,.0f}'.format(balance).replace(' ', '')
                    else:
                        balance = '{:7,.2f}'.format(balance).replace(' ', '')
            else:
                balance = 0
                
            balances.append({
                'currency': item,
                'balance': balance,
            })
        else:
            balances.append({
                'currency': item,
                'balance': 0,
            })

    context = {
        'balances': balances,
    }

    return render(request, 'trading/wallet.html', context=context)


def bill(request, bill_type, pk):

    if request.POST:
        if request.POST.get('type') == 'send_accept':
            send_id = request.POST.get('send_id')
            send = Send.objects.filter(pk=send_id).first()
            if send:
                if send.receiver.pk == request.user.pk:
                    balance = Balance_update.objects.filter(
                        trader=send.trader, currency=send.currency, payed=True
                    ).aggregate(Sum('amount'))['amount__sum']
                    if not balance:
                        balance = 0
                    
                    if balance < send.amount:
                        messages.error(request, sender_no_balance_msg.get(send.trader, 'ru'))
                        return redirect(request.path)

                    send.accepted = True
                    send.save()

                    plus_balance = Balance_update(
                        trader=send.receiver,
                        update_type='plus',
                        currency=send.currency,
                        amount=send.amount,
                        confirmed=True,
                        payed=True,
                    )
                    plus_balance.save()
                    
                    minus_balance = Balance_update(
                        trader=send.trader,
                        update_type='minus',
                        currency=send.currency,
                        amount=send.amount,
                        confirmed=True,
                        payed=True,
                    )
                    minus_balance.save()

                    notification = Notification.objects.filter(
                        Q(_type='send_sender')
                        &
                        Q(trader=send.trader)
                        &
                        Q(foreign_object_id=send.pk)
                    ).first()
                    if notification:
                        notification.status = 'accepted'
                        notification.save()
                    else:
                        notification = Notification(
                            _type='send_sender',
                            trader=send.trader,
                            foreign_object_id=send.pk,
                            status='accepted',
                        )
                        notification.save()

                    notification = Notification.objects.filter(
                        Q(_type='send_receiver')
                        &
                        Q(trader=send.receiver)
                        &
                        Q(foreign_object_id=send.pk)
                    ).first()
                    if notification:
                        notification.status = 'accepted'
                        notification.save()
                    else:
                        notification = Notification(
                            _type='send_receiver',
                            trader=send.receiver,
                            foreign_object_id=send.pk,
                            status='accepted',
                        )
                        notification.save()
                    
                    try:
                        bot = TeleBot(settings.BOT_TOKEN)
                        keyb = accepted_btns(send.trader.bot_lang_code)
                        bot.edit_message_reply_markup(send.receiver.bot_user_id, send.message_id, reply_markup=keyb)
                    except:
                        pass

        elif request.POST.get('type') == 'send_deny':
            send_id = request.POST.get('send_id')
            send = Send.objects.filter(pk=send_id).first()
            if send:
                if send.receiver.pk == request.user.pk:
                    send.denied = True
                    send.save()

                    notification = Notification.objects.filter(
                        Q(_type='send_sender')
                        &
                        Q(trader=send.trader)
                        &
                        Q(foreign_object_id=send.pk)
                    ).first()
                    if notification:
                        notification.status = 'denied'
                        notification.save()
                    else:
                        notification = Notification(
                            _type='send_sender',
                            trader=send.trader,
                            foreign_object_id=send.pk,
                            status='denied',
                        )
                        notification.save()

                    notification = Notification.objects.filter(
                        Q(_type='send_receiver')
                        &
                        Q(trader=send.receiver)
                        &
                        Q(foreign_object_id=send.pk)
                    ).first()
                    if notification:
                        notification.status = 'denied'
                        notification.save()
                    else:
                        notification = Notification(
                            _type='send_receiver',
                            trader=send.receiver,
                            foreign_object_id=send.pk,
                            status='denied',
                        )
                        notification.save()
                    
                    try:
                        bot = TeleBot(settings.BOT_TOKEN)
                        keyb = denied_btns(send.trader.bot_lang_code)
                        bot.edit_message_reply_markup(send.receiver.bot_user_id, send.message_id, reply_markup=keyb)
                    except:
                        pass

        return redirect(request.path)

    if bill_type == 'exchange':
        bill_object = Exchange.objects.filter(pk=pk).first()
        if bill_object is None:
            return redirect('main')

        fees = (bill_object.fees * 100) - 100

        # Rate format
        rate = bill_object.rate
        if rate > 1:
            rate = '{:,.1f}'.format(rate)
        else:
            precision = int(str(rate).split('-')[1]) + 1
            rate = "{:.{}f}".format(rate, round(precision))

        rate_currency_from = bill_object.currency_from.name
        rate_currency_to = bill_object.currency_to.name

        # Currencies
        currency_from = bill_object.currency_from.name
        currency_to = bill_object.currency_to.name
        
        # Prices
        amount_1 = bill_object.amount_input
        amount_2 = bill_object.amount_output
        
        # Change values if exchange_type is buy
        if bill_object.exchange_type == 'buy' and bill_object.currency_type == 'fiat':
            
            # Currencies
            currency_to = bill_object.currency_from.name
            currency_from = bill_object.currency_to.name
            
            # Prices
            amount_1 = bill_object.amount_output
            amount_2 = bill_object.amount_input

        # Initial prices
        initial_amount_1 = amount_1 / bill_object.fees
        initial_amount_2 = amount_2

        if amount_1 > 1:
            if are_decimal_digits_zero(amount_1):
                amount_1 = '{:,.0f}'.format(amount_1).replace(' ', '')
            else:
                amount_1 = '{:,.2f}'.format(amount_1).replace(' ', '')
        if amount_2 > 1:
            if are_decimal_digits_zero(amount_2):
                amount_2 = '{:,.0f}'.format(amount_2).replace(' ', '')
            else:
                amount_2 = '{:,.2f}'.format(amount_2).replace(' ', '')

        if initial_amount_1 > 1:
            if are_decimal_digits_zero(initial_amount_1):
                initial_amount_1 = '{:,.0f}'.format(initial_amount_1).replace(' ', '')
            else:
                initial_amount_1 = '{:,.2f}'.format(initial_amount_1).replace(' ', '')
        if initial_amount_2 > 1:
            if are_decimal_digits_zero(initial_amount_2):
                initial_amount_2 = '{:,.0f}'.format(initial_amount_2).replace(' ', '')
            else:
                initial_amount_2 = '{:,.2f}'.format(initial_amount_2).replace(' ', '')

        bill_container = {
            'id': bill_object.pk,
            'hash': bill_object.trader.hash_code,
            'currency_from': currency_from,
            'currency_to': currency_to,
            'initial_amount_1': initial_amount_1,
            'initial_amount_2': initial_amount_2,
            'fees': fees,
            'amount_1': amount_1,
            'amount_2': amount_2,
            'rate': f"1 {rate_currency_from} - {rate} {rate_currency_to}",
            'time': _('30 seconds'),
            'bill_type': _('Exchange'),
        }

    elif bill_type == 'withdraw':
        bill_object = Withdraw.objects.filter(pk=pk).first()
        if bill_object is None:
            return redirect('main')
        
        fees = (bill_object.fees * 100) - 100

        amount = bill_object.amount
        initial_amount = bill_object.amount / bill_object.fees
        fee_amount = amount - initial_amount

        if amount > 1:
            if are_decimal_digits_zero(amount):
                amount = '{:,.0f}'.format(amount).replace(' ', '')
            else:
                amount = '{:,.2f}'.format(amount).replace(' ', '')

        if initial_amount > 1:
            if are_decimal_digits_zero(initial_amount):
                initial_amount = '{:,.0f}'.format(initial_amount).replace(' ', '')
            else:
                initial_amount = '{:,.2f}'.format(initial_amount).replace(' ', '')

        if fee_amount > 1:
            if are_decimal_digits_zero(fee_amount):
                fee_amount = '{:,.0f}'.format(fee_amount).replace(' ', '')
            else:
                fee_amount = '{:,.2f}'.format(fee_amount).replace(' ', '')
        else:
            fee_amount = '{:,.2f}'.format(fee_amount).strip()

        bill_container = {
            'id': bill_object.pk,
            'hash': bill_object.trader.hash_code,
            'currency': bill_object.currency.name,
            'initial_amount': initial_amount,
            'fees': fees,
            'fee_amount': fee_amount,
            'amount': bill_object.amount,
            'credit_card': bill_object.credit_card,
            'wallet': bill_object.wallet,
            'time': _('2 hours'),
            'bill_type': _('Withdraw'),
        }

    elif bill_type == 'send':
        bill_object = Send.objects.filter(pk=pk).first()
        if bill_object is None:
            return redirect('main')
        
        viewer = request.GET.get('viewer')

        amount = bill_object.amount
        if amount > 1:
            if are_decimal_digits_zero(amount):
                amount = '{:,.0f}'.format(amount).replace(' ', '')
            else:
                amount = '{:,.2f}'.format(amount).replace(' ', '')

        bill_container = {
            'id': bill_object.pk,
            'sender_hash': bill_object.trader.hash_code,
            'receiver_hash': bill_object.receiver.hash_code,
            'currency': bill_object.currency.name,
            'amount': amount,
            'time': _('30 seconds'),
            'bill_type': _('Send'),
            'viewer': viewer,
            'accepted': bill_object.accepted,
            'denied': bill_object.denied,
        }

    elif bill_type == 'balance':
        bill_object = Balance_update.objects.filter(pk=pk).first()
        if bill_object is None:
            return redirect('main')
        
        amount = bill_object.amount
        if amount > 1:
            if are_decimal_digits_zero(amount):
                amount = '{:,.0f}'.format(amount).replace(' ', '')
            else:
                amount = '{:,.2f}'.format(amount).replace(' ', '')

        bill_container = {
            'id': bill_object.pk,
            'hash': bill_object.trader.hash_code,
            'currency': bill_object.currency.name,
            'amount': amount,
            'payment_type': bill_object.payment_type,
            'time': _('30 seconds'),
            'bill_type': _('Balance update'),
        }

    elif bill_type == 'subscription':
        bill_object = Subscription.objects.filter(pk=pk).first()
        if bill_object is None:
            return redirect('main')
        
        price = bill_object.price
        if price > 1:
            if are_decimal_digits_zero(price):
                price = '{:,.0f}'.format(price).replace(' ', '')
            else:
                price = '{:,.2f}'.format(price).replace(' ', '')

        bill_container = {
            'id': bill_object.pk,
            'hash': bill_object.trader.hash_code,
            'subscription_type': bill_object.subscription_type.new_name,
            'subscription_period': bill_object.subscription_period,
            'currency': bill_object.currency.name,
            'price': price,
            'payment_type': bill_object.payment_type,
            'time': _('30 seconds'),
            'bill_type': _('Subscription'),
        }

    else:
        return redirect('main')

    context = {
        'bill_type': bill_type,
        'bill': bill_container,
    }

    return render(request, 'trading/bill.html', context=context)


def rate_templates(request):

    if not request.user.is_superuser:
        return redirect('main')

    if request.POST:
        template = None
        if request.POST.get('template_id'):
            template = Rate_template.objects.filter(pk=request.POST.get('template_id')).first()
            if template:
                template.currency_to_id = request.POST.get('currency_to_id')
                template.amount = request.POST.get('amount')
                template.save()
        else:
            currency_from_id = request.POST.get('currency_from_id')
            currency_to_id = request.POST.get('currency_to_id')
            amount = request.POST.get('amount')
            template = Rate_template(
                currency_from_id=currency_from_id,
                currency_to_id=currency_to_id,
                amount=float(amount),
            )
            template.save()

        response = redirect('rate-templates')
        if template is not None:
            response['location'] += f"?currency_type={template.currency_from.currency_type}&currency_id={template.currency_from.pk}"
        return response

    currency_type = request.GET.get('currency_type')
    if currency_type not in ['fiat', 'crypto']:
        currency_type = 'fiat'
    
    current_currencies = Currency.objects.filter(currency_type=currency_type, status=True)

    current_currency = None
    if request.GET.get('currency_id'):
        current_currency = current_currencies.filter(pk=request.GET.get('currency_id')).first()
    
    if current_currency == None:
        current_currency = current_currencies.first()

    context = {
        'currency_type': currency_type,
        'current_currencies': current_currencies,
        'current_currency': current_currency,
        'fiat_currencies': Currency.objects.filter(status=True, currency_type='fiat'),
        'crypto_currencies': Currency.objects.filter(status=True, currency_type='crypto'),
        'fiat_templates': Rate_template.objects.filter(currency_from=current_currency, currency_to__currency_type='fiat'),
        'crypto_templates': Rate_template.objects.filter(currency_from=current_currency, currency_to__currency_type='crypto'),
    }

    return render(request, 'trading/rate-templates.html', context=context)
