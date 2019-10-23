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
                                unique=True)

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
    currency = models.CharField(verbose_name='Transaction currency',
                                max_length=30)

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

    def __repr__(self):
        return f'InputTransaction ({self.id}, {self.currency})'


class OutPutTransaction(TransactionBase):

    class Meta:
        verbose_name = 'OutPut Transaction'
        verbose_name_plural = 'OutPut Transactions'

    def __repr__(self):
        return f'OutPutTransaction ({self.id}, {self.currency})'


class ExchangeHistory(Base):

    ACTIVE, FINISHED = 1, 2

    EXCHANGE_STATUTES = (
        (ACTIVE, 'Active'),
        (FINISHED, 'Finished'),
    )

    user_email = models.EmailField(verbose_name='Email of user')

    fee = models.DecimalField(verbose_name='Transaction fee',
                              max_digits=16,
                              decimal_places=8,
                              default=0)

    from_currency = models.CharField(verbose_name='Currency from',
                                     max_length=30)

    to_currency = models.CharField(verbose_name='Currency to',
                                   max_length=30)

    issue_rate = models.DecimalField(verbose_name='Rate in usd',
                                     max_digits=16,
                                     decimal_places=8)

    transaction_input = models.OneToOneField(InputTransaction,
                                             null=True,
                                             blank=True,
                                             on_delete=models.SET_NULL)

    transaction_output = models.OneToOneField(OutPutTransaction,
                                              null=True,
                                              blank=True,
                                              on_delete=models.SET_NULL)

    status = models.SmallIntegerField(choices=EXCHANGE_STATUTES,
                                      default=ACTIVE,
                                      db_index=True)

    amount = models.DecimalField(verbose_name='Exchange amount',
                                 max_digits=16,
                                 decimal_places=5)

    def __repr__(self):
        return f'History id: {self.id} bound with user {self.user_email}'

    class Meta:
        verbose_name = 'Exchange History'
        verbose_name_plural = 'Exchange Histories'


class PlatformWallet(Base):

    address = models.CharField(verbose_name='Wallet address',
                               max_length=100,
                               unique=True)

    currency = models.CharField(verbose_name='Wallet currency_slug',
                                max_length=40)

    is_active = models.BooleanField(verbose_name='Is active wallet',
                                    default=True)

    def __repr__(self):
        return f'Wallet id: {self.id} currency {self.currency}'

    class Meta:
        verbose_name = 'Platform Wallet'
        verbose_name_plural = 'Platform Wallets'
