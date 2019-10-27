import typing
from abc import ABC
from exchanger import models
from exchanger import utils
from exchanger.gateway import wallets_service_gw
__STATES_TRANSACTIONS__ = {

}


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
    ):
        """
        Update exchange_objects current state to self. Raise if restricted.
         Update exchange_object related parameters. Commit.
        """
        cls.validate(exchange_object)
        exchange_object.status = cls.id
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
            stop_status = None,
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

        return stop_status is not None and next_state.id == stop_status.value

    @staticmethod
    def check_new_state(
            from_state: typing.Type['State'],
            to_state: typing.Type['State'],
            same=True
    ) -> bool:

        if same is True and from_state == to_state:
            return True
        return to_state in __STATES_TRANSACTIONS__[from_state]


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


class NewState(State):
    id: models.ExchangeHistory.NEW

    @classmethod
    def set(
            cls,
            exchange_object: models.ExchangeHistory,
            **params
    ):

        wallet = models.PlatformWallet.objects.get(
            currency__name=exchange_object.from_currency,
            currency__active=True,
            is_active=True,
        )
        exchange_object.wallet = wallet

        return exchange_object.state

    @classmethod
    def _inner_transition(
            cls,
            exchange_object: models.ExchangeHistory
    ):
        resp = wallets_service_gw.put_on_monitoring(
            external_id=exchange_object.wallet_id,
            address=exchange_object.wallet.address,
        )


def state_by_status(status: typing.Union[int, State]):
    __CLASSES__ = {c.id: c for c in utils.all_subclasses(State)}
    return __CLASSES__[getattr(status, 'value', status)]
