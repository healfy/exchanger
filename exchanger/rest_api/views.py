from rest_framework import viewsets

from exchanger.models import (
    ExchangeHistory
)

from .serializers import (
    ExchangeHistorySerializer,
)


class ExchangeHistoryViewSet(viewsets.ModelViewSet):
    queryset = ExchangeHistory.objects.all()
    serializer_class = ExchangeHistorySerializer
