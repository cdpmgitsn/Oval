from django.db import models
from django.urls import reverse
from apps.trading.models import Trader
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):

    notification_type = (
        ('exchange', 'Exchange'),
        ('withdraw', 'Withdraw'),
        ('send_sender', 'Send sender'),
        ('send_receiver', 'Send receiver'),
        ('subscription', 'Subscription'),
        ('balance_update', 'Balance update'),
    )

    status_types = (
        ('accepted', 'Accepted'),
        ('pending', 'Pending'),
        ('denied', 'Denied'),
    )

    _type = models.CharField("Тип уведомления", max_length=255, choices=notification_type)
    trader = models.ForeignKey(Trader, on_delete=models.RESTRICT, verbose_name="Трейдер")
    foreign_object_id = models.BigIntegerField("ID внешнего объекта", default=0)
    status = models.CharField("Статус", max_length=255, choices=status_types, default='pending')
    date = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        ordering = ['-date',]
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    @property
    def message(self):
        result = _("New notification")

        if self.status == "accepted":
            if self._type == "exchange":
                result = _("Exchange request accepted")
            elif self._type == "withdraw":
                result = _("Withdrawal request accepted")
            elif self._type == "send_sender":
                result = _("Money sent successfully")
            elif self._type == "send_receiver":
                result = _("Money received successfully")
            elif self._type == "subscription":
                result = _("Subscription activated")
            elif self._type == "balance_update":
                result = _("Balance updated")
        elif self.status == "pending":
            if self._type == "exchange":
                result = _("Exchange request pending")
            elif self._type == "withdraw":
                result = _("Withdrawal request pending")
            elif self._type == "send_sender":
                result = _("Money sending pending")
            elif self._type == "send_receiver":
                result = _("Money receiving pending")
            elif self._type == "subscription":
                result = _("Subscription pending")
            elif self._type == "balance_update":
                result = _("Balance update pending")
        elif self.status == "denied":
            if self._type == "exchange":
                result = _("Exchange request denied")
            elif self._type == "withdraw":
                result = _("Withdrawal request denied")
            elif self._type == "send_sender":
                result = _("Money sending denied")
            elif self._type == "send_receiver":
                result = _("Money receiving denied")
            elif self._type == "subscription":
                result = _("Subscription denied")
            elif self._type == "balance_update":
                result = _("Balance update denied")

        return result

    @property
    def url(self):
        if self.foreign_object_id:
            notification_type = ''
            if self._type == 'exchange':
                notification_type = 'exchange'
            elif self._type == 'withdraw':
                notification_type = 'withdraw'
            elif self._type in ['send_sender', 'send_receiver']:
                notification_type = 'send'
            elif self._type == 'subscription':
                notification_type = 'subscription'
            elif self._type == 'balance_update':
                notification_type = 'balance'
            if notification_type:
                return reverse('bill', kwargs={'bill_type': notification_type, 'pk': self.foreign_object_id})
        return ''

    def __str__(self) -> str:
        return self._type
