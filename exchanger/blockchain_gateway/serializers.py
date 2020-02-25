import pytz
from datetime import datetime
from django.conf import settings
from rest_framework import serializers


class BGWTransactionSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False)
    from_ = serializers.CharField()
    to = serializers.CharField()
    currencySlug = serializers.CharField()
    time = serializers.IntegerField()
    value = serializers.DecimalField(decimal_places=8, max_digits=12)
    hash = serializers.CharField()
    isOutput = serializers.BooleanField(default=False)
    fee = serializers.DecimalField(decimal_places=8, max_digits=12,
                                   required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # hack for parse 'from' value from response
        for name in list(self.fields.keys()):
            if name.endswith("_"):
                field = self.fields.pop(name)
                self.fields[name[:-1]] = field

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
        if self.instance.from_address != data['from_']:
            raise serializers.ValidationError(
                f"Invalid transaction hash {data['hash']}"
            )
        time_created = datetime.fromtimestamp(int(data['time'])).replace(
                tzinfo=pytz.utc)
        delta = datetime.now().replace(tzinfo=pytz.utc) - time_created
        total_minutes, second = divmod(delta.seconds, 60)
        if total_minutes > settings.TRANSACTION_DELTA:
            raise serializers.ValidationError(
                f"Invalid transaction hash {data['hash']}"
            )
        return data
