import typing
import logging
from abc import ABC
from decimal import Decimal
from decimal import ROUND_HALF_UP
from django.conf import settings
from exchanger import models
from exchanger import utils
from exchanger.gateway import wallets_service_gw
from exchanger.gateway import currency_service_gw
from exchanger.gateway import trx_service_gw
from exchanger.currencies_gateway import CurrenciesServiceGateway
from exchanger.transactions_gateway import TransactionsServiceGateway
from exchanger.gateway.base import BaseRepr

logger = logging.getLogger('exchanger.log')


class State(BaseRepr, ABC):
    """
    Abstract class for exchange_object states.
    Used to implement transitions between states of a exchange_object,
    update exchange_object parameters
    """

    id: typing.Optional[int] = None

    @classmethod
    def validate(
            cls,
            exchange_object: models.ExchangeHistory,
            raise_exception=True
    ) -> bool:
        """
        returns True if new state can be set
        """
        valid = cls.check_new_state(exchange_object.state, cls)
        if raise_exception and not valid:
            raise ValueError(
                f'Сan not update the state {exchange_object.state}. '
                f'Transition to state {cls} is prohibited.')
        return valid

    @classmethod
    @utils.nested_commit_on_success
    def set(
            cls,
            exchange_object: models.ExchangeHistory,
            **params
    ) -> typing.Type['State']:
        """
        Update exchange_objects current state to self. Raise if restricted.
         Update exchange_object related parameters. Commit.
        """
        cls.validate(exchange_object)
        exchange_object.status = cls.id
        exchange_object.save()
        return exchange_object.state

    @classmethod
    def make_inner_transition(
            cls,
            exchange_object: models.ExchangeHistory,
            stop_status=None
    ) -> typing.NoReturn:

        """ExchangeHistory internal update method
        (all data is obtained inside the method).
        Get new state with internal update method,
        checks stop, and continue internal update for new state if necessary.
        """
        next_state = cls._inner_transition(exchange_object)
        if next_state == cls or cls._check_stop(next_state, stop_status):
            return
        return next_state.make_inner_transition(exchange_object,
                                                stop_status=stop_status)

    @classmethod
    def make_outer_transition(
            cls,
            exchange_object: models.ExchangeHistory,
            stop_status=None,
            **params
    ) -> typing.NoReturn:

        """ExchangeHistory external update method (all data is passes from
        external sources in the method **params).
        Get new state with external update method, checks stop,
        and continue internal update for new state if necessary.
        """
        next_state = cls._outer_transition(exchange_object, **params)
        if next_state == cls or cls._check_stop(next_state, stop_status):
            return
        return next_state.make_inner_transition(exchange_object,
                                                stop_status=stop_status)

    @classmethod
    def _inner_transition(
            cls,
            exchange_object: models.ExchangeHistory
    ) -> typing.Type['State']:

        return cls

    @classmethod
    def _outer_transition(
            cls,
            exchange_object: models.ExchangeHistory,
            **params
    ) -> typing.Type['State']:

        return cls

    @classmethod
    def _check_stop(
            cls,
            next_state,
            stop_status
    ) -> bool:

        return stop_status is not None and next_state.id == stop_status

    @staticmethod
    def check_new_state(
            from_state: typing.Type['State'],
            to_state: typing.Type['State'],
            same=True
    ) -> bool:

        if same is True and from_state == to_state:
            return True
        return to_state in __STATES_TRANSACTIONS__[from_state]


class SetWalletMixin:
    """
    Mixin class to set wallets on exchange object
    Object have 2 types of wallet:

    ingoing_wallet - Wallet for which we will expect a transfer from the user
     Calculated from parameter from_currency

    outgoing_wallet - Wallet from which we will transfer money in a
     successful scenario
     Calculated from parameter to_currency

    """
    query = models.PlatformWallet.objects.filter(is_active=True)
    default = 'ethereum'

    attrs = [
        {'from_currency': 'ingoing_wallet'},
        {'to_currency': 'outgoing_wallet'}
    ]

    @classmethod
    def set_wallet(
            cls,
            instance: models.ExchangeHistory
    ) -> typing.NoReturn:

        for attr in cls.attrs:
            for key, value in attr.items():
                currency = getattr(instance, key)
                slug = cls.default if not currency.is_bitcoin else currency.slug
                setattr(instance, value, cls.query.get(currency__slug=slug))


class SetTransactionMixin:
    """
    Mixin class for set transaction to exchange object

    model: one of two existing model(InputTransaction, OutPutTransaction)
    trx_attr: ont of two attributes of instance ExchangeHistory -
    transaction_input (for input transactions)
    transaction_output (for output transactions)

    """
    model: typing.Type['models.TransactionBase']
    trx_attr: str

    @classmethod
    def set_transaction(
            cls,
            instance: models.ExchangeHistory,
            **params
    ) -> typing.NoReturn:

        setattr(instance, cls.trx_attr, cls.model.objects.create(**params))


class ValidateInputTransactionMixin:
    """
    Mixin class to validate input transaction value. If the user transfer us
    a smaller value from the expected value, we must recalculate the commission,
     as well as the size of the outgoing transfer
    """

    gw: CurrenciesServiceGateway

    # noinspection PyUnresolvedReferences
    @classmethod
    def set(
            cls,
            exchange_object: models.ExchangeHistory,
            **params
    ) -> typing.Type['State']:

        cls.validate(exchange_object)
        return super().set(exchange_object, **params)

    @classmethod
    def validate(
            cls,
            exchange_object: models.ExchangeHistory
    ) -> typing.NoReturn:

        input_transaction = exchange_object.transaction_input

        if not input_transaction.value == exchange_object.ingoing_amount:
            slug = input_transaction.currency.slug
            rates = {_['slug']: _['rate'] for _ in cls.gw.get_currencies()}
            usd_value = (Decimal(rates.get(slug)) * input_transaction.value
                         ).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
            fee = utils.calculate_fee(usd_value, rates, slug)
            exchange_object.fee = fee
            exchange_object.outgoing_amount = cls.calc_outgoing_amount(
                usd_value, rates, fee, exchange_object.to_currency.slug)

    @classmethod
    def calc_outgoing_amount(
            cls,
            usd_amount: Decimal,
            rates: typing.Dict,
            fee: Decimal,
            slug: str
    ) -> Decimal:
        return Decimal((usd_amount - fee) / Decimal(rates.get(slug)))


class CreateTransferMixin:
    """
    Mixin class to create payment by external service
    Connecting with service transactions by class trx_service_gw

    next_state: state to which following exchange object
    wallet_type: one two types of wallet associated with the exchange object
    There are two cases here:

     if it successfully direction we are sending money from cold wallet
     associated with currency which user want to buy(outgoing_wallet),
     recalculate transaction fee

     if it failure direction we are sending money from wallet to which the user
     transferred the deposit (ingoing wallet)
    """

    next_state: typing.Type['State']
    wallet_type: str
    set_fee: bool
    gw: TransactionsServiceGateway()

    @classmethod
    def _inner_transition(
            cls,
            exchange_object: models.ExchangeHistory
    ) -> typing.Type['State']:

        wallet_id = getattr(exchange_object, cls.wallet_type)
        transfer = exchange_object.transaction_output.transfer_dict()

        cls.gw.create_transfer(
            wallet_id=wallet_id,
            **transfer
        )
        return cls.next_state.set(exchange_object)


class ConfirmTransactionMixin:

    """
    Mixin class for confirm transaction associated with exchange object

    trx_attr: ont of two attributes of instance ExchangeHistory -
    transaction_input (for input transactions)
    transaction_output (for output transactions)
    next_state: state to which following exchange object
    """

    trx_attr: str
    next_state: typing.Type['State']

    @classmethod
    def _inner_transition(
            cls,
            exchange_object: models.ExchangeHistory
    ) -> typing.Union[typing.Type['State'], object]:

        trx = getattr(exchange_object, cls.trx_attr)

        if trx.status == models.TransactionBase.CONFIRMED and trx.trx_hash:
            return cls.next_state.set(exchange_object)
        return cls


# States
class UnknownState(State):
    """Default state for not - created exchange ."""
    id = models.ExchangeHistory.UNKNOWN

    @classmethod
    def _inner_transition(
            cls,
            exchange_object: models.ExchangeHistory
    ) -> typing.Type['State']:

        return NewState.set(exchange_object)


class NewState(State,
               SetTransactionMixin,
               SetWalletMixin):

    """
    Initial state for exchange object
    There are three steps that we must to do.
    1. set ingoing and outgoing wallets
    2. set input transaction
    3. sent to wallets service params of input transaction that we are expected
    from user

    """

    id = models.ExchangeHistory.NEW
    model = models.InputTransaction
    trx_attr = 'transaction_input'

    @classmethod
    def set(
            cls,
            exchange_object: models.ExchangeHistory,
            **params
    ) -> typing.Type['State']:

        cls.set_wallet(exchange_object)
        cls.set_transaction(
            exchange_object,
            value=exchange_object.ingoing_amount,
            to_address=exchange_object.ingoing_wallet.address,
            from_address=exchange_object.from_address,
            currency=exchange_object.from_currency
        )
        logger.info(f'Created new exchange operation with params: \n'
                    f'{exchange_object.to_info_message}')
        return super().set(exchange_object)

    @classmethod
    def _inner_transition(
            cls,
            exchange_object: models.ExchangeHistory
    ) -> typing.Type['State']:

        wallets_service_gw.put_on_monitoring(
            wallet_id=exchange_object.ingoing_wallet.external_id,
            wallet_address=exchange_object.ingoing_wallet.address,
            expected_currency=exchange_object.transaction_input.currency.slug,
            expected_address=exchange_object.transaction_input.from_address,
            expected_amount=exchange_object.transaction_input.value,
            uuid=exchange_object.transaction_input.uuid
        )

        return WaitingDepositState.set(exchange_object)


class WaitingDepositState(State):
    """
    State in which we are waiting money(deposit) transfer from user
    """

    id = models.ExchangeHistory.WAITING_DEPOSIT
    gw = currency_service_gw

    @classmethod
    def _inner_transition(
            cls,
            exchange_object: models.ExchangeHistory
    ) -> typing.Type['State']:

        trx = exchange_object.transaction_input

        if trx.status == models.TransactionBase.CONFIRMED and trx.trx_hash:
            if cls.validate_value(trx):
                return DepositPaidState.set(exchange_object)
            return InsufficientDepositState.set(exchange_object)
        return cls

    @classmethod
    def validate_value(cls, trx: models.InputTransaction) -> bool:
        slug = trx.currency.slug
        rates = {_['slug']: _['rate'] for _ in cls.gw.get_currencies()}
        usd_value = (Decimal(rates.get(slug)) * trx.value
                     ).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
        return usd_value > settings.DEFAULT_FEE


# Failed states case

class FailedState(State):
    """
    Failure case.
    Final state in failure case
    """
    id = models.ExchangeHistory.FAILED


class ReturningDepositState(ConfirmTransactionMixin,
                            State):
    """
    Failure case.
    State in which we has already created output transaction from platform
    wallet to which user sent deposit and we are waiting to confirm out
    transaction
    """
    id = models.ExchangeHistory.RETURNING_DEPOSIT
    next_state = FailedState
    trx_attr = 'transaction_output'


class InsufficientDepositState(CreateTransferMixin,
                               State,
                               SetTransactionMixin):
    """
    Failure case.
    State in which user has already sent deposit to platform wallet but the
    amount appears insufficient and we want to abort exchange operation and
    send user money back
    """

    id = models.ExchangeHistory.INSUFFICIENT_DEPOSIT
    model = models.OutPutTransaction
    wallet_type = 'ingoing_wallet_id'
    trx_attr = 'transaction_output'
    next_state = ReturningDepositState
    gw = trx_service_gw

    @classmethod
    def set(
            cls,
            exchange_object: models.ExchangeHistory,
            **params
    ) -> typing.Type['State']:

        cls.set_transaction(
            exchange_object,
            value=exchange_object.transaction_input.value,
            from_address=exchange_object.ingoing_wallet.address,
            to_address=exchange_object.from_address,
            currency=exchange_object.transaction_input.currency
        )
        return super().set(exchange_object)


# Success states cases

class DepositPaidState(State):
    """
    Successful case.
    State in which user has already sent deposit to platform wallet and the
    amount appears sufficient
    """
    id = models.ExchangeHistory.DEPOSIT_PAID

    @classmethod
    def _inner_transition(
            cls,
            exchange_object: models.ExchangeHistory
    ) -> typing.Type['State']:

        return CalculatingState.set(exchange_object)


class CalculatingState(ValidateInputTransactionMixin,
                       State):
    """
    Successful case.
    State in which we are validating input transaction amount and recalculating
    out going amount and transaction fee if it necessary

    """
    id = models.ExchangeHistory.CALCULATING
    gw = currency_service_gw

    @classmethod
    def _inner_transition(
            cls,
            exchange_object: models.ExchangeHistory
    ) -> typing.Type['State']:

        return CreatingOutGoingState.set(exchange_object)


class ClosedState(State):
    """
    Successful case.
    Final state in successfully direction
    """
    id = models.ExchangeHistory.CLOSED


class OutgoingRunningState(ConfirmTransactionMixin,
                           State):

    """
    Successful case.
    State in which we has already created output transaction from platform
    and we are waiting to confirm out transaction
    """
    id = models.ExchangeHistory.OUTGOING_RUNNING
    trx_attr = 'transaction_output'
    next_state = ClosedState


class CreatingOutGoingState(CreateTransferMixin,
                            State,
                            SetTransactionMixin):
    """
    Successful case.
    State in which we set output transaction to exchange object and
    creating money transfer by external service "Transactions".
    We must also set a transaction fee and fix the exchange rate of
    the US dollar to the issue currency
    """

    id = models.ExchangeHistory.CREATING_OUTGOING_TRANSFER
    model = models.OutPutTransaction
    trx_attr = 'transaction_output'
    wallet_type = 'outgoing_wallet_id'
    next_state = OutgoingRunningState
    gw = trx_service_gw

    @classmethod
    def set(
            cls,
            exchange_object: models.ExchangeHistory,
            **params
    ) -> typing.Type['State']:

        cls.set_transaction(
            exchange_object,
            value=exchange_object.outgoing_amount,
            from_address=exchange_object.outgoing_wallet.address,
            to_address=exchange_object.to_address,
            currency=exchange_object.to_currency
        )
        return super().set(exchange_object)


def state_by_status(status: typing.Union[int, State]) -> typing.Type['State']:
    __CLASSES__ = {c.id: c for c in utils.all_subclasses(State)}
    return __CLASSES__[getattr(status, 'value', status)]


__STATES_TRANSACTIONS__ = {
    UnknownState: [NewState],
    NewState: [WaitingDepositState],
    WaitingDepositState: [DepositPaidState, InsufficientDepositState],
    DepositPaidState: [CalculatingState],
    CalculatingState: [CreatingOutGoingState],
    InsufficientDepositState: [ReturningDepositState],
    ReturningDepositState: [FailedState],
    CreatingOutGoingState: [OutgoingRunningState],
    OutgoingRunningState: [ClosedState],
}
