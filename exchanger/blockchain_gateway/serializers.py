import pytz
from datetime import datetime
from django.conf import settings
from rest_framework import serializers

from exchanger.rpc.blockchain_gateway_pb2 import ResponseStatus


class BGWTransactionSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False)
    from_ = serializers.CharField()
    to = serializers.CharField()
    currencySlug = serializers.CharField()
    time = serializers.IntegerField()
    hash = serializers.CharField()
    isOutput = serializers.BooleanField(default=False)
    status = serializers.CharField()

    default_error_messages = {
        'invalid_hash': "Invalid transaction hash {hash_}"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # hack for parse 'from' value from response
        for name in list(self.fields.keys()):
            if name.endswith("_"):
                field = self.fields.pop(name)
                self.fields[name[:-1]] = field

    def validate(self, data):
        data = super().validate(data)

        time_created = datetime.fromtimestamp(int(data['time'])).replace(
                tzinfo=pytz.utc)
        delta = datetime.now().replace(tzinfo=pytz.utc) - time_created
        total_minutes, second = divmod(delta.seconds, 60)
        if any([
            self.instance.currency.slug.lower() != data['currencySlug'].lower(),
            self.instance.to_address.lower() != data['to'].lower(),
            self.instance.from_address.lower() != data['from_'].lower(),
            ResponseStatus.Value(data['status']) == ResponseStatus.NOT_FOUND,
            total_minutes > settings.TRANSACTION_DELTA
        ]):
            self.fail('invalid_hash', hash_=data['hash'])
        return data
