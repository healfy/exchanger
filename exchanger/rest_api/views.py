from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from exchanger import states
from exchanger.models import (
    ExchangeHistory
)

from .serializers import (
    ExchangeHistorySerializer,
)


class ExchangeHistoryViewSet(viewsets.ModelViewSet):
    queryset = ExchangeHistory.objects.all()
    serializer_class = ExchangeHistorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        exchange_object = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        states.NewState.set(exchange_object)

        exchange_object.request_update(
            stop_status=ExchangeHistory.WAITING_DEPOSIT)

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: 'OK'}
    )
    @action(methods=['get'], detail=True)
    def refresh(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.request_update()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)