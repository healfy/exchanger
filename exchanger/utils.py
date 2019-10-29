from django.db import transaction


def nested_commit_on_success(func):
    def _nested_commit_on_success(*args, **kwds):
        with transaction.atomic():
            return func(*args, **kwds)

    return _nested_commit_on_success


def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]
