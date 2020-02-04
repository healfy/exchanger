from django.db import transaction
from decimal import Decimal
from decimal import ROUND_HALF_UP
from django.conf import settings


def nested_commit_on_success(func):
    def _nested_commit_on_success(*args, **kwds):
        with transaction.atomic():
            return func(*args, **kwds)

    return _nested_commit_on_success


def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]


def calculate_fee(amount: Decimal, rates: dict, slug: str) -> Decimal:
    amount_in_usd = amount * Decimal(rates[slug])
    return Decimal(settings.TRX_FEE_DICT[amount_in_usd >
                                         settings.MIN_FEE_LIMIT])


def quantize(value: Decimal) -> Decimal:
    return value.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
