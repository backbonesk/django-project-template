from http import HTTPStatus
from typing import Union

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import UserModel
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext as _
from apps.core.models import Token
from apps.api.errors import ProblemDetailException

User = get_user_model()


class BaseBackend:
    def authenticate(self, request, email=None, password=None, **kwargs) -> Union[User, AnonymousUser]:
        if email is None:
            email = kwargs.get(UserModel.USERNAME_FIELD)
        if email is None or password is None:
            return AnonymousUser()
        try:
            user = UserModel._default_manager.get_by_natural_key(email)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return AnonymousUser()

    @staticmethod
    def user_can_authenticate(user):
        is_active = getattr(user, "is_active", None)
        return is_active or is_active is None


class BearerBackend(BaseBackend):
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


class BasicBackend(BaseBackend):
    def authenticate(self, request, **kwargs) -> User:
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


__all__ = [
    'BaseBackend',
    'BasicBackend',
    'BearerBackend',
]
