import os
import redis_lock
import redis_namespace
from contextlib import contextmanager

from django.conf import settings


REDIS_HOST = os.environ.get('REDIS_HOST', settings.REDIS_HOST)
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', settings.REDIS_PASSWORD)


def connect_redis() -> redis_namespace.StrictRedis:
    return redis_namespace.StrictRedis(
        host=REDIS_HOST,
        password=REDIS_PASSWORD,
        namespace=settings.REDIS_NAMESPACE
    )


def request_key(*req):
    """
        format key for caching
    """
    return '::'.join(
        ('exchanger_service',) + tuple(str(v) for v in req)) + '::'


class ManualLockGateway:
    """Set db lock with lock|unlock methods (instead context manager)"""
    max_timeout = 120

    def __init__(self, red: redis_namespace.StrictRedis):
        self.redis = red
        self._lock = None

    def lock(self, name: str, blocking: bool = False):
        if self._lock is not None:
            raise Exception(
                f'{self.__class__.__name__}: can not lock. '
                f'Manual lock is already locked by '
                f'{self._lock}, unlock at first.')
        self._lock = redis_lock.Lock(self.redis, request_key(name),
                                     expire=self.max_timeout)
        return self._lock.acquire(blocking=blocking)

    def unlock(self, strict: bool = True):
        if self._lock is None:
            if strict:
                raise Exception(
                    f'{self.__class__.__name__}: can not unlock, '
                    f'lock at first.')
            return
        self._lock.release()
        self._lock = None


@contextmanager
def nowait_lock(connection) -> ManualLockGateway:
    locker = ManualLockGateway(connection)
    try:
        yield locker
    finally:
        locker.unlock()
