from django.db import models
from datetime import datetime


class BaseQuerySet(models.query.QuerySet):

    def get_queryset(self):
        return self.filter(is_deleted=False)

    def delete(self):
        return self.update(is_deleted=True, deleted_at=datetime.now())


class BaseManager(models.Manager):
    def get_queryset(self):
        return BaseQuerySet(
            self.model, using=self._db).filter(is_deleted=False)

    def delete(self):
        return BaseQuerySet(
            self.model, using=self._db).update(is_deleted=True,
                                               deleted_at=datetime.now())


class CurrencyManager(BaseManager):
    def get_queryset(self):
        query = super().get_queryset()
        return query.filter(active=True)
