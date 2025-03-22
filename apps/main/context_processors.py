from apps.about.models import About
from apps.trading.models import Trader
from apps.notification.models import Notification


def load_company_data(request):

    trader = Trader.objects.filter(pk=request.user.id).first()
    notifications = Notification.objects.filter(trader=trader)

    context = {
        'trader': trader,
        'company': About.objects.first(),
        'notifications_count': notifications.filter(status='pending').count(),
        'last_notifications': notifications[:5],
    }

    return context
