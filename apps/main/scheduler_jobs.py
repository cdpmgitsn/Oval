from apps.trading.models import Trader
from apps.subscription.models import Subscription_update, Subscription_type
from datetime import date, timedelta, datetime


def decrease_subscription():
    traders = [
        item
        for item in Trader.objects.all()
        if item.current_subscription_type['status'] in ['pro', 'medium']
    ]
    date_limit = datetime.now() - timedelta(days=1)
    for item in traders:
        status = item.current_subscription_type['status']
        last_update = Subscription_update.objects.filter(
            trader=item,
            subscription_type__name=status,
            update_type='minus',
            days=1,
            date__gte=date_limit
        ).last()
        if not last_update:
            subscription_type = Subscription_type.objects.filter(name=status).first()
            new_update = Subscription_update(
                trader=item,
                subscription_type=subscription_type,
                update_type='minus',
                days=1,
            )
            new_update.save()
