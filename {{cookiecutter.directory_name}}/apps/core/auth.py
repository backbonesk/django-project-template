from typing import Union

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.core.models import Token, User

User = get_user_model()


class BearerBackend(ModelBackend):
    @staticmethod
    def _by_token(token) -> Union[User, None]:
        try:
            token_obj = Token.objects.get(pk=token)
        except (Token.DoesNotExist, ValidationError):
            return None

        token_obj.user.last_login = timezone.now()
        token_obj.user.save()

        return token_obj.user

    def authenticate(self, request, **kwargs) -> Union[User, None]:
        if kwargs.get('bearer'):
            return self._by_token(kwargs.get('bearer'))
        else:
            return super().authenticate(request, **kwargs)
