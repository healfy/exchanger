
from rest_framework import serializers
from exchanger.models import (
    InputTransaction,
    OutPutTransaction,
    ExchangeHistory
)


class InputTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InputTransaction
        fields = '__all__'


class OutPutTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutPutTransaction
        fields = '__all__'


class ExchangeHistorySerializer(serializers.ModelSerializer):

    transaction_input = InputTransactionSerializer(read_only=True, many=True)
    transaction_output = OutPutTransactionSerializer(read_only=True, many=True)

    class Meta:
        model = ExchangeHistory
        fields = ('user_email', 'from_currency', 'transaction_output',
                  'to_currency', 'status', 'amount', 'transaction_input')
