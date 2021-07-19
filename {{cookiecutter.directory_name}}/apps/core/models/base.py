import uuid

from django.db import models
from django.utils import timezone

from apps.core.managers.base import BaseManager
from apps.core.managers.soft_delete import SoftDeleteManager


class SoftDeleteMixin(models.Model):
    class Meta:
        abstract = True

    deleted_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager(alive_only=False)

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save()

    def hard_delete(self):
        super(SoftDeleteMixin, self).delete()


class UpdatedAtMixin(models.Model):
    class Meta:
        abstract = True

    updated_at = models.DateTimeField(auto_now=True)


class BaseModel(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BaseManager()

    def update(self, data: dict):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()


__all__ = [
    'SoftDeleteMixin',
    'UpdatedAtMixin',
    'BaseModel'
]
