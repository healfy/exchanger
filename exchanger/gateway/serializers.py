from rest_framework import serializers
from .base import BaseRepr


class TransactionSerializer(BaseRepr,
                            serializers.Serializer):

    trx_hash = serializers.CharField(max_length=100)
    uuid = serializers.CharField(max_length=100)


class TransactionDataSerializer(BaseRepr,
                                serializers.Serializer):
    transactions = TransactionSerializer(many=True)
