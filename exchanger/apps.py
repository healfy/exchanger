from django.apps import AppConfig
from exchanger.gateway import start_remote_gateways


class ExchangerConfig(AppConfig):
    name = 'exchanger'

    def ready(self):
        start_remote_gateways()
