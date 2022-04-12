from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.user import User
from apps.core.models.base import BaseModel


class Token(BaseModel):
    class Meta:
        app_label = 'core'
        db_table = 'tokens'
        default_permissions = ()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens', verbose_name=_('token_user'))
    expires_at = models.DateTimeField(null=True, verbose_name=_('token_expires_at'))


__all__ = [
    'Token'
]
