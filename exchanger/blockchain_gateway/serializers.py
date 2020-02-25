import pytz
from datetime import datetime
from django.conf import settings
from rest_framework import serializers
from exchanger.models import InputTransaction


class BGWTransactionSerializer(serializers.Serializer):

    class Meta:
        model = InputTransaction
        exclude = '__all__'

    id = serializers.IntegerField(required=False)
    from_address = serializers.CharField(source='from')
    to = serializers.CharField()
    currencySlug = serializers.CharField()
    time = serializers.IntegerField()
    value = serializers.DecimalField(decimal_places=8, max_digits=12)
    hash = serializers.CharField()
    isOutput = serializers.BooleanField(default=False)
    fee = serializers.DecimalField(decimal_places=8, max_digits=12,
                                   required=False)

    def validate(self, data):
        data = super().validate(data)
        if self.instance.currency.slug != data['currencySlug']:
            raise serializers.ValidationError(
                f"Invalid transaction hash {data['hash']}"
            )
        if self.instance.to_address != data['to']:
            raise serializers.ValidationError(
                f"Invalid transaction hash {data['hash']}"
            )
        if self.instance.from_address != data['from_address']:
            raise serializers.ValidationError(
                f"Invalid transaction hash {data['hash']}"
            )
        time_created = datetime.fromtimestamp(int(data['time'])).replace(
                tzinfo=pytz.utc)
        delta = datetime.now().replace(tzinfo=pytz.utc) - time_created
        if delta.min > settings.TRANSACTION_DELTA:
            raise serializers.ValidationError(
                f"Invalid transaction hash {data['hash']}"
            )
        return data
