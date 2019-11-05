
from rest_framework import serializers
from exchanger.models import (
    InputTransaction,
    OutPutTransaction,
    ExchangeHistory
)


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
