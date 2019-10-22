

from rest_framework import serializers
from exchanger.models import (
    Transaction,
    ExchangeHistory
)


class ExchangeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeHistory
        fields = ('user_email', 'from_currency', 'to_currency')
