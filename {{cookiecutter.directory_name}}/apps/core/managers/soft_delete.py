from apps.core.managers.base import BaseManager
from apps.core.querysets.soft_delete import SoftDeleteQuerySet


class SoftDeleteManager(BaseManager):
    def __init__(self, *args, **kwargs):
        self._alive_only = kwargs.pop('alive_only', True)
        super(SoftDeleteManager, self).__init__(*args, **kwargs)

    def hard_delete(self):
        return self.get_queryset().hard_delete()

    def get_queryset(self):
        if self._alive_only:
            return SoftDeleteQuerySet(self.model).alive()
        return SoftDeleteQuerySet(self.model)
