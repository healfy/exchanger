from django.db import transaction
from decimal import Decimal
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
    amount_in_usd = amount * rates[slug]
    return settings.TRX_FEE_DICT[amount_in_usd > settings.MIN_FEE_LIMIT]
