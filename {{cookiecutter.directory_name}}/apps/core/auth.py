from http import HTTPStatus
from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext as _

from apps.core.models import Token
from apps.api.errors import ProblemDetailException

User = get_user_model()


class BearerBackend(ModelBackend):
    @staticmethod
    def _by_token(token) -> Optional[User]:
        try:
            token_obj = Token.objects.get(pk=token)
        except (Token.DoesNotExist, ValidationError):
            return None

        token_obj.user.last_login = timezone.now()
        token_obj.user.save()

        return token_obj.user

    def authenticate(self, request, **kwargs) -> Optional[User]:
        if kwargs.get('bearer'):
            user = self._by_token(kwargs.get('bearer'))
        else:
            user = super().authenticate(request, **kwargs)

        return user


class BasicBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        user = super().authenticate(request, **kwargs)

        if not user:
            raise ProblemDetailException(
                request,
                _('Invalid credentials'),
                status=HTTPStatus.UNAUTHORIZED,
                extra_headers=(
                    ('WWW-Authenticate', f'Bearer realm="{slugify(settings.INSTANCE_NAME)}"'),
                )
            )
        return user
