import uuid
import typing
from datetime import datetime
from django.db import models


class Base(models.Model):

    created_at = models.DateTimeField(verbose_name='Time of created',
                                      default=datetime.now,
                                      db_index=True)

    updated_at = models.DateTimeField(verbose_name='Time of last update',
                                      null=True,
                                      blank=True)

    def save(self, **kwargs):
        self.updated_at = datetime.now()
        super().save(**kwargs)

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class Currency(Base):

    name = models.CharField(verbose_name='Currency name',
                            max_length=20)

    slug = models.CharField(verbose_name='Currency slug',
                            max_length=20)

    active = models.BooleanField(verbose_name='it is used',
                                 default=True)

    is_token = models.BooleanField(verbose_name='Is token currency',
                                   default=False)

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'

    def __str__(self):
        return f'{self.name}'


class TransactionBase(Base):

    SUCCESS, NOT_FOUND, FAILED, CONFIRMED, PENDING, NEW = 1, 2, 3, 4, 5, 6

    STATUTES = (
        (SUCCESS, 'SUCCESS'),
        (NOT_FOUND, 'NOT_FOUND'),
        (FAILED, 'FAILED'),
        (CONFIRMED, 'CONFIRMED'),
        (PENDING, 'PENDING'),
        (NEW, 'NEW'),
    )

    trx_hash = models.CharField(verbose_name='Transaction hash',
                                max_length=100,
                                db_index=True,
                                unique=True,
                                null=True,
                                blank=True)

    value = models.DecimalField(verbose_name='Transaction amount',
                                max_digits=16,
                                decimal_places=5)

    to_address = models.CharField(verbose_name='Address to which the '
                                               'currency will transfer',
                                  max_length=100)

    from_address = models.CharField(verbose_name='Address from the '
                                                 'currency will transfer',
                                    max_length=100)

    status = models.SmallIntegerField(verbose_name='Transaction status',
                                      choices=STATUTES,
                                      default=NEW,
                                      db_index=True)

    confirmed_at = models.DateTimeField(verbose_name='Datetime transaction '
                                                     'confirmed',
                                        null=True,
                                        blank=True,
                                        db_index=True)
    currency = models.OneToOneField(Currency,
                                    verbose_name='Transaction currency',
                                    on_delete=models.CASCADE,
                                    related_name='%(app_label)s_%(class)s_'
                                                 'related')

    uuid = models.UUIDField(verbose_name='Internal hash for identification trx',
                            default=uuid.uuid4)

    def confirm(self,
                status: int,
                time_confirmed: typing.Optional[datetime] = None
                ) -> typing.NoReturn:

        if status == self.CONFIRMED:
            self.confirmed_at = time_confirmed if time_confirmed \
                else datetime.now()
            self.save()

    class Meta:
        abstract = True


class InputTransaction(TransactionBase):

    class Meta:
        verbose_name = 'Input Transaction'
        verbose_name_plural = 'Input Transactions'

    def __str__(self):
        return f'InputTransaction ({self.id}, {self.currency})'


class OutPutTransaction(TransactionBase):

    class Meta:
        verbose_name = 'OutPut Transaction'
        verbose_name_plural = 'OutPut Transactions'

    def __str__(self):
        return f'OutPutTransaction ({self.id}, {self.currency})'


class PlatformWallet(Base):

    address = models.CharField(verbose_name='Wallet address',
                               max_length=100,
                               unique=True)

    currency = models.ForeignKey(Currency,
                                 verbose_name='Wallet currency_slug',
                                 on_delete=models.CASCADE,
                                 related_name='wallets')

    is_active = models.BooleanField(verbose_name='Is active wallet',
                                    default=True)

    def __str__(self):
        return f'Wallet id: {self.id} currency {self.currency}'

    class Meta:
        verbose_name = 'Platform Wallet'
        verbose_name_plural = 'Platform Wallets'


class ExchangeHistory(Base):

    UNKNOWN = 0
    NEW = 1
    WAITING_DEPOSIT = 2
    INSUFFICIENT_DEPOSIT = 3
    DEPOSIT_PAID = 4
    CREATING_OUTGOING_TRANSFER = 5
    OUTGOING_RUNNING = 6
    CLOSED = 7
    FAILED = 8

    EXCHANGE_STATUTES = (
        (UNKNOWN, 'UNKNOWN STATUS'),
        (NEW, 'NEW'),
        (WAITING_DEPOSIT, 'WAITING MONEY FROM USER'),
        (INSUFFICIENT_DEPOSIT, 'MONEY TRANSFER IS INSUFFICIENT'),
        (DEPOSIT_PAID, 'DEPOSIT_PAID'),
        (CREATING_OUTGOING_TRANSFER, 'CREATING MONEY TRANSFER TO USER'),
        (OUTGOING_RUNNING, 'TRANSFER IN STATUS SUCCESS'),
        (CLOSED, 'EXCHANGE IS GONE'),
        (FAILED, 'FAILED EXCHANGE'),
    )

    user_email = models.EmailField(verbose_name='Email of user')

    fee = models.DecimalField(verbose_name='Transaction fee',
                              max_digits=16,
                              decimal_places=8,
                              default=0)

    from_currency = models.ForeignKey(Currency,
                                      verbose_name='Currency from',
                                      on_delete=models.CASCADE,
                                      related_name='exchange_history')

    to_currency = models.ForeignKey(Currency,
                                    verbose_name='Currency to',
                                    on_delete=models.CASCADE)

    issue_rate = models.DecimalField(verbose_name='Rate in usd',
                                     max_digits=16,
                                     decimal_places=8,
                                     default=0)

    transaction_input = models.OneToOneField(InputTransaction,
                                             null=True,
                                             blank=True,
                                             on_delete=models.SET_NULL,
                                             related_name='exchange_history')

    transaction_output = models.OneToOneField(OutPutTransaction,
                                              null=True,
                                              blank=True,
                                              on_delete=models.SET_NULL,
                                              related_name='exchange_history')

    status = models.SmallIntegerField(choices=EXCHANGE_STATUTES,
                                      default=UNKNOWN,
                                      db_index=True)

    ingoing_amount = models.DecimalField(verbose_name='From exchange amount',
                                         max_digits=16,
                                         decimal_places=5)

    outgoing_amount = models.DecimalField(verbose_name='To exchange amount',
                                          max_digits=16,
                                          decimal_places=5)

    wallet = models.ForeignKey(PlatformWallet,
                               verbose_name='Which wallet does '
                                            'the current transaction belong to',
                               null=True,
                               blank=True,
                               on_delete=models.SET_NULL,
                               related_name='exchange_history')

    from_address = models.CharField(verbose_name='Address from we are '
                                                 'expect trx',
                                    max_length=50)

    @property
    def state(self):
        from exchanger import states
        """
            one of State in states.py
        """
        return states.state_by_status(self.status)

    def request_update(self, stop_status: int = None):
        """Update  state with state inner transition. Commit.
        Should use for initiative update without params.
        :param stop_status status u want to stop, if None forward if possible.
        """
        self.state.make_inner_transition(self, stop_status=stop_status)

    def outer_update(self, stop_status: int = None, **params):
        """Update loan state with state outer transition. Commit.
        Should use for update state with some result from asynchronous task. Update parameters are passing using params.
        :param stop_status status u want to stop, if None forward if possible.
        """
        self.state.make_outer_transition(self, stop_status=stop_status, **params)

    def __str__(self):
        return f'Exchange history id: {self.id} bound with user' \
               f' {self.user_email}'

    class Meta:
        verbose_name = 'Exchange History'
        verbose_name_plural = 'Exchange Histories'
