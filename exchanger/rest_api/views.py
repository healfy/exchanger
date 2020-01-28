from django.conf import settings
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from exchanger import states
from exchanger.currencies_gateway.serializers import CurrencySerializer
from exchanger.gateway import currency_service_gw
from exchanger.models import (
    ExchangeHistory,
    Currency
)

from .serializers import (
    ExchangeHistorySerializer,
    SettingsSerializer
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

    @swagger_auto_schema(
        deprecated=True
    )
    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @swagger_auto_schema(
        deprecated=True
    )
    def partial_update(self, request, *args, **kwargs):
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

    @swagger_auto_schema(
        deprecated=True
    )
    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().list(request, *args, **kwargs)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CurrencyServiceView(APIView):

    @swagger_auto_schema(responses={200: CurrencySerializer})
    def get(self, request, format=None):

        data = [
            elem for elem in currency_service_gw.get_currencies()
            if Currency.objects.filter(slug=elem['slug']).exists()
        ]
        return Response(data)


class SettingsView(APIView):
    serializer = SettingsSerializer

    @swagger_auto_schema(responses={status.HTTP_200_OK: SettingsSerializer})
    def get(self, request):
        data = self.serializer(data={
            'default': settings.DEFAULT_FEE,
            'extended': settings.EXTENDED_FEE,
            'limit': settings.MIN_FEE_LIMIT,
                              }).initial_data
        return Response(data)
