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
    def authenticate(self, request, **kwargs) -> User:
        try:
            token = Token.objects.get(pk=kwargs['bearer'])
        except (Token.DoesNotExist, ValidationError):
            raise ProblemDetailException(
                request,
                _('Invalid Bearer Token'),
                status=HTTPStatus.UNAUTHORIZED,
            )

        if not self.user_can_authenticate(token.user):
            raise ProblemDetailException(request, _('Inactive user.'), status=HTTPStatus.FORBIDDEN)

        token.user.last_login = timezone.now()
        token.user.save()

        request.token = token

        return token.user


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
