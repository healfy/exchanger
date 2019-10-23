import sys
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from exchanger.gateway.grpc_server import serve_forever


class Command(BaseCommand):
    help = 'api server'

    def handle(self, *args, **options):
        with serve_forever():
            self.stdout.write(self.style.SUCCESS('Successfully started grpc server '))
            try:
                while True:
                    time.sleep(settings.ONE_DAY_IN_SECONDS)
            except KeyboardInterrupt:
                pass
