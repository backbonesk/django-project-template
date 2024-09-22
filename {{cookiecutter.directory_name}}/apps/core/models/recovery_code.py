from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.base import BaseModel
from apps.core.models.user import User


class RecoveryCode(BaseModel):
    class Meta:
        app_label = 'core'
        db_table = 'recovery_codes'
        default_permissions = ()

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recovery_codes', verbose_name=_('recovery_code_user')
    )


__all__ = [
    'RecoveryCode'
]
