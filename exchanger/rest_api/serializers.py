from django.conf import settings
from rest_framework import serializers
from exchanger.models import (
    InputTransaction,
    OutPutTransaction,
    ExchangeHistory
)
from exchanger.gateway import bgw_service_gw


class InputTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InputTransaction
        exclude = InputTransaction.BASE_FIELDS


class OutPutTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutPutTransaction
        exclude = OutPutTransaction.BASE_FIELDS


class ExchangeHistorySerializer(serializers.ModelSerializer):

    transaction_input = InputTransactionSerializer(read_only=True)
    transaction_output = OutPutTransactionSerializer(read_only=True)

    class Meta:
        model = ExchangeHistory
        fields = ('id', 'user_email', 'from_currency', 'transaction_output',
                  'to_currency', 'status', 'ingoing_amount',
                  'transaction_input', 'outgoing_amount', 'ingoing_wallet',
                  'outgoing_wallet', 'from_address', 'to_address', 'fee')

    def validate(self, attrs):
        data = super().validate(attrs)
        if not settings.TEST_MODE:
            return self.bgw_validate_addresses(data)
        return data

    @staticmethod
    def get_attrs(data: dict, address: str, currency: str) -> dict:
        return {
                'address': data[address],
                'currency_slug': data[currency].slug
            }

    def bgw_validate_addresses(self, data: dict) -> dict:
        attrs = ['from', 'to']
        for attr in attrs:
            resp = bgw_service_gw.check_address(**self.get_attrs(
                data, f'{attr}_address', f'{attr}_currency'))

            if not resp.get('isinstance'):
                raise serializers.ValidationError(
                    f'You address {data[f"{attr}_address"]} is not valid'
                )
        return data
