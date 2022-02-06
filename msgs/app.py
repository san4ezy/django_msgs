from django.apps import AppConfig


class MSGSConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'msgs'

    def ready(self):
        # import apps.deposit.signals
        pass
