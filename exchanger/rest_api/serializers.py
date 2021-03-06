import typing
from decimal import Decimal
from django.conf import settings
from django.db.models import ObjectDoesNotExist
from rest_framework import serializers

from exchanger.utils import quantize
from exchanger.utils import calculate_fee
from exchanger.currencies_gateway import CurrenciesServiceGateway
from exchanger.blockchain_gateway import BlockChainServiceGateway

from exchanger.models import (
    InputTransaction,
    OutPutTransaction,
    ExchangeHistory,
    Currency
)
from exchanger.gateway import (
    bgw_service_gw,
    currency_service_gw,
)


class ExternalServicesValidatorMixin:

    b_gw: BlockChainServiceGateway = bgw_service_gw
    currencies: CurrenciesServiceGateway = currency_service_gw

    @staticmethod
    def get_attrs(data: dict, address: str, currency: str) -> dict:
        return {
                'address': data[address],
                'currency_slug': data[currency].slug
            }

    def bgw_validate_addresses(self, data: dict) -> dict:
        for attr in ['from', 'to']:
            resp = self.b_gw.check_address(**self.get_attrs(
                data, f'{attr}_address', f'{attr}_currency'))

            if not resp.get('isinstance'):
                raise serializers.ValidationError(
                    f'You address {data[f"{attr}_address"]} is not valid'
                )
        return data

    def external_svc_validate(self, data: dict):
        rates = {_['slug']: _['rate'] for _ in self.currencies.get_currencies()}
        self.bgw_validate_addresses(data)
        self.update_rates(data, rates)
        return data

    @staticmethod
    def update_rates(
            data: dict,
            data_rates: dict,
    ) -> dict:

        input_slug = data['from_currency'].slug
        current_rate_from = Decimal(data_rates.get(input_slug))

        output_slug = data['to_currency'].slug
        current_rate_to = Decimal(data_rates.get(output_slug))

        usd_value_from = quantize(
            Decimal(current_rate_from * Decimal(data['ingoing_amount'])))

        if usd_value_from > settings.MAX_SUM:
            raise serializers.ValidationError(
                f'Max input value is {settings.MAX_SUM}'
            )

        usd_fee = calculate_fee(usd_value_from, data_rates, output_slug)
        if usd_value_from - usd_fee <= 0:
            raise serializers.ValidationError(
                f'{output_slug} : "{usd_value_from}" is to low for exchanger ')

        data['fee'] = quantize(Decimal(usd_fee / current_rate_from))

        data['issue_rate_from'] = current_rate_from
        data['issue_rate_to'] = current_rate_to
        data['outgoing_amount'] = quantize(
            Decimal((usd_value_from - usd_fee) / current_rate_to))
        return data


class InputTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InputTransaction
        exclude = InputTransaction.BASE_FIELDS


class OutPutTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutPutTransaction
        exclude = OutPutTransaction.BASE_FIELDS


class ExchangeHistorySerializer(serializers.ModelSerializer,
                                ExternalServicesValidatorMixin):

    transaction_input = InputTransactionSerializer(read_only=True)
    transaction_output = OutPutTransactionSerializer(read_only=True)
    from_currency = serializers.CharField(required=True)
    to_currency = serializers.CharField(required=True)

    class Meta:
        model = ExchangeHistory
        exclude = ExchangeHistory.BASE_FIELDS + ('id', )

    def validate(self, attrs):
        data = super().validate(attrs)
        if not settings.TEST_MODE:
            try:
                return self.external_svc_validate(data)
            except Exception as exc:
                raise serializers.ValidationError(exc)
        data['to_address'] = data['to_address'].lower()
        data['from_address'] = data['from_address'].lower()
        return data

    def validate_from_currency(
            self,
            slug: str
    ) -> typing.Union[Currency, typing.NoReturn]:
        try:
            return Currency.objects.get(slug=slug)
        except ObjectDoesNotExist as e:
            raise serializers.ValidationError(e)

    def validate_to_currency(
            self,
            slug: str
    ) -> typing.Union[Currency, typing.NoReturn]:
        try:
            return Currency.objects.get(slug=slug)
        except ObjectDoesNotExist as e:
            raise serializers.ValidationError(e)

    def validate_ingoing_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError(f'Invalid ingoing '
                                              f'amount {float(amount)}')
        return amount

    def validate_outgoing_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError(f'Invalid outgoing amount'
                                              f' {float(amount)}')
        return amount

    def validate_from_address(self, address: str):
        if not address:
            raise serializers.ValidationError('Required field from_address')
        return address

    def validate_to_address(self, address: str):
        if not address:
            raise serializers.ValidationError('Required field to_address')
        return address

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.uuid
        return data


class SettingsSerializer(serializers.Serializer):
    default = serializers.IntegerField()
    extended = serializers.IntegerField()
    limit = serializers.IntegerField()
    max_sum = serializers.IntegerField()
    delta = serializers.IntegerField()


class TrxHashSerializer(serializers.Serializer):

    trx_hash = serializers.CharField()

    class Meta:
        model = InputTransaction
        exclude = '__all__'

    def validate_trx_hash(self, _hash: str):
        if self.Meta.model.objects.filter(trx_hash=_hash).exists():
            return serializers.ValidationError(
                f'Transaction with hash {_hash} already in base'
            )
        return _hash
