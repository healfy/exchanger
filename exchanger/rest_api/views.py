import typing
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
from exchanger.gateway import bgw_service_gw
from exchanger.models import (
    ExchangeHistory,
    Currency
)

from .serializers import (
    ExchangeHistorySerializer,
    SettingsSerializer,
    TrxHashSerializer
)


class UpdateTrxMixin:

    get_object: typing.Callable
    get_serializer: typing.Callable
    additional_serializer = TrxHashSerializer

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: 'OK'},
        request_body=TrxHashSerializer
    )
    @action(methods=['post'], detail=True)
    def update_transaction(self, request, *args, **kwargs):
        instance = self.get_object()
        trx_hash = self.get_trx_hash(request)
        self.validate_hash(instance, trx_hash)
        instance.set_input_transaction_hash(trx_hash=trx_hash)
        instance.request_update()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_trx_hash(self, request) -> str:
        """
        Check hash is not exists in database
        :return: trx_hash
        """
        serializer = self.additional_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.data['trx_hash']

    @staticmethod
    def validate_hash(instance: ExchangeHistory, trx_hash) -> typing.NoReturn:
        """
        Validate hash in blockchain

        :param instance: ExchangeHistory object
        :param trx_hash: transaction hash
        """
        currency_slug = instance.transaction_input.currency.slug
        to_address = instance.transaction_input.to_address
        input_trx = instance.transaction_input
        serializer = bgw_service_gw.get_transaction(
            trx_hash, currency_slug, to_address, input_trx)
        serializer.is_valid(raise_exception=True)


class ExchangeHistoryViewSet(viewsets.ModelViewSet,
                             UpdateTrxMixin):

    queryset = ExchangeHistory.objects.all()
    serializer_class = ExchangeHistorySerializer
    lookup_field = 'uuid'

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
            if elem['slug'] in Currency.objects.values_list('slug', flat=True)
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
            'max_sum': settings.MAX_SUM,
            'delta': settings.DELTA,
                              }).initial_data
        return Response(data)
