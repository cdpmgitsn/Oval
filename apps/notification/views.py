from django.shortcuts import render
from django.urls import reverse
from apps.trading.models import Trader
from apps.notification.models import Notification


def notifications(request):

    trader = Trader.objects.filter(pk=request.user.id).first()

    context = {
        'notifications': Notification.objects.filter(trader=trader),
    }

    return render(request, 'notification/notifications.html', context=context)
