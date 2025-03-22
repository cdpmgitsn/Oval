from django.apps import AppConfig


class SubscriptionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.subscription'

    def ready(self) -> None:
        import apps.subscription.signals
