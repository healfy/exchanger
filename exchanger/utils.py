import sys
import warnings
import logging
import typing
from functools import wraps

from django.core.mail import send_mail
from django.db import transaction
from decimal import Decimal
from decimal import ROUND_HALF_UP
from django.conf import settings
from django.template.loader import render_to_string


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


def all_kwargs_required(func):

    """
    Only works with new style functions def foo(*, **kwargs): pass
    first argument " * " say that function allows only keyword arguments
    If python version < 3.6 validating is passed
    """

    @wraps(func)
    def _wrapper(*args, **kwargs):

        expect_major = 3
        expect_minor = 6
        current_version = str(sys.version_info[0]
                              )+"."+str(sys.version_info[1]
                                        )+"."+str(sys.version_info[2])

        if sys.version_info[:2] != (expect_major, expect_minor):
            warnings.warn(
                "Current Python version was unexpected and "
                " ---all_kwargs_required--- function doesnt work:"
                " Python " + current_version)
            return func(*args, **kwargs)

        for param in func.__kwdefaults__:
            if param not in kwargs:
                raise ValueError(f'named argument {param} of '
                                 f'function "{func.__name__}" is required')
            if not kwargs.get(param, None):
                raise ValueError(f'value of argument {param}: --[{kwargs.get(param, None)}]-- in '
                                 f'function "{func.__name__}" is required')
        return func(*args, **kwargs)
    return _wrapper


def send_mail_to_user(exchanger):

    use_https = settings.DEFAULT_HOST == 'app.bonumchain.com'
    send_to = exchanger.user_email
    context = {
        'default_host': settings.DEFAULT_HOST,
        'uuid': exchanger.uuid,
        'protocol': 'https' if use_https else 'http',
        'email': send_to
    }

    try:
        send_mail(
            'New exchange operation is created',
            '',
            settings.DEFAULT_FROM_EMAIL,
            [send_to],
            html_message=render_to_string(
                'exchanger_mail.html', context),
        )
    except Exception as e:
        logger = logging.getLogger('exchanger')
        logger.error(f'send email to {send_to} failed {e}')
