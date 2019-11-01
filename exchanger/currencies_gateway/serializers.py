from rest_framework import serializers


class CoefficientSerializer(serializers.Serializer):

    days = serializers.IntegerField(required=False)

    collateral_coefficient = serializers.FloatField(
        source='collateralCoefficient', required=False)

    mandatory_coefficient = serializers.FloatField(
        source='mandatoryCoefficient', required=False)

    warning_coefficient = serializers.FloatField(
        source='warningCoefficient', required=False)


class CurrencySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    fullname = serializers.CharField(required=False)
    slug = serializers.CharField(required=True)
    rate = serializers.CharField(required=True)
    coefficients = CoefficientSerializer(many=True, required=False)
