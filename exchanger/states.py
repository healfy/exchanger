import typing
import logging
from abc import ABC
from exchanger import models
from exchanger import utils
from exchanger.gateway import wallets_service_gw


logger = logging.getLogger('exchanger.log')


class State(ABC):
    """
    Abstract class for exchange_object states.
    Used to implement transitions between states of a exchange_object,
    update exchange_object parameters, monitor asynchronous results
    (transactions, verification statuses).
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
    @utils.nested_commit_on_success
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
    @utils.nested_commit_on_success
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
    query = models.PlatformWallet.objects.filter(is_active=True)
    default = 'ethereum'

    @classmethod
    def set_wallet(
            cls,
            instance: models.ExchangeHistory
    ) -> typing.NoReturn:

        currency = instance.from_currency
        slug = cls.default if not currency.is_bitcoin else currency.slug
        instance.wallet = cls.query.get(currency__slug=slug)


class SetTransactionMixin:
    model: typing.Type['models.TransactionBase']
    trx_attr: str

    @classmethod
    def set_transaction(
            cls,
            instance: models.ExchangeHistory,
            **params
    ) -> typing.NoReturn:

        setattr(instance, cls.trx_attr, cls.model.objects.create(**params))


class ConfirmTransactionMixin:
    trx_attr: str
    next_state: typing.Type['State']

    @classmethod
    def _inner_transition(
            cls,
            exchange_object: models.ExchangeHistory
    ) -> typing.Union[typing.Type['State'], object]:

        trx = getattr(exchange_object, cls.trx_attr)

        if trx.status == models.TransactionBase.CONFIRMED:
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
    """

    id = models.ExchangeHistory.NEW
    model = models.InputTransaction

    @classmethod
    def set(
            cls,
            exchange_object: models.ExchangeHistory,
            **params
    ):
        cls.set_wallet(exchange_object)
        cls.set_transaction(
            exchange_object,
            value=exchange_object.ingoing_amount,
            to_address=exchange_object.wallet.address,
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
            wallet_id=exchange_object.wallet.external_id,
            wallet_address=exchange_object.wallet.address,
            expected_currency=exchange_object.transaction_input.currency.slug,
            expected_address=exchange_object.transaction_input.from_address,
            expected_amount=exchange_object.transaction_input.value,
            uuid=exchange_object.transaction_input.uuid
        )

        return WaitingDepositState.set(exchange_object)


class WaitingDepositState(State):

    id = models.ExchangeHistory.WAITING_DEPOSIT

    @classmethod
    def _inner_transition(
            cls,
            exchange_object: models.ExchangeHistory
    ) -> typing.Type['State']:

        trx = exchange_object.transaction_input

        if trx.status == models.TransactionBase.CONFIRMED:
            if cls.validate_amount(trx):
                return DepositPaidState.set(exchange_object)
            return InsufficientDepositState.set(exchange_object)
        return cls

    @classmethod
    def validate_amount(
            cls,
            transaction:  models.InputTransaction
    ) -> bool:
        """
        :TODO logic to validate input amount
        :param transaction:
        :return:
        """
        return True


# Failed states case


class InsufficientDepositState(State,
                               SetTransactionMixin):

    id = models.ExchangeHistory.INSUFFICIENT_DEPOSIT
    model = models.OutPutTransaction
    trx_attr = 'transaction_output'

    @classmethod
    def set(
            cls,
            exchange_object: models.ExchangeHistory,
            **params
    ) -> typing.Type['State']:

        cls.set_transaction(
            exchange_object,
            value=exchange_object.transaction_input.value,
            from_address=exchange_object.wallet.address,
            to_address=exchange_object.from_address,
            currency=exchange_object.transaction_input.currency
        )
        return super().set(exchange_object)

    @classmethod
    def _inner_transition(
            cls,
            exchange_object: models.ExchangeHistory
    ) -> typing.Type['State']:
        """
        :TODO logic to connect with transaction server
        :param exchange_object:
        :return:
        """
        return ReturningDepositState.set(exchange_object)


class FailedState(State):
    id = models.ExchangeHistory.FAILED


class ReturningDepositState(ConfirmTransactionMixin,
                            State):

    id = models.ExchangeHistory.RETURNING_DEPOSIT
    next_state = FailedState
    trx_attr = 'transaction_output'


# Success states cases

class DepositPaidState(State):
    id = models.ExchangeHistory.DEPOSIT_PAID

    @classmethod
    def _inner_transition(
            cls,
            exchange_object: models.ExchangeHistory
    ) -> typing.Type['State']:
        return CreatingOutGoingState.set(exchange_object)


class CreatingOutGoingState(State,
                            SetTransactionMixin):

    id = models.ExchangeHistory.CREATING_OUTGOING_TRANSFER
    model = models.OutPutTransaction
    trx_attr = 'transaction_output'

    @classmethod
    def set(
            cls,
            exchange_object: models.ExchangeHistory,
            **params
    ) -> typing.Type['State']:

        cls.set_transaction(
            exchange_object,
            value=exchange_object.outgoing_amount,
            from_address=exchange_object.wallet.address,
            to_address=exchange_object.to_address,
            currency=exchange_object.to_currency
        )
        return super().set(exchange_object)

    @classmethod
    def _inner_transition(
            cls,
            exchange_object: models.ExchangeHistory
    ) -> typing.Type['State']:
        """
        :TODO logic to connect with transaction server
        :param exchange_object:
        :return:
        """
        return OutgoingRunningState.set(exchange_object)


class ClosedState(State):
    id = models.ExchangeHistory.CLOSED


class OutgoingRunningState(ConfirmTransactionMixin,
                           State):
    id = models.ExchangeHistory.OUTGOING_RUNNING
    trx_attr = 'transaction_output'
    next_state = ClosedState


def state_by_status(status: typing.Union[int, State]):
    __CLASSES__ = {c.id: c for c in utils.all_subclasses(State)}
    return __CLASSES__[getattr(status, 'value', status)]


__STATES_TRANSACTIONS__ = {
    NewState: [WaitingDepositState],
    WaitingDepositState: [DepositPaidState, InsufficientDepositState],
    DepositPaidState: [CreatingOutGoingState],
    InsufficientDepositState: [ReturningDepositState],
    ReturningDepositState: [FailedState],
    CreatingOutGoingState: [OutgoingRunningState],
    OutgoingRunningState: [ClosedState],
}
