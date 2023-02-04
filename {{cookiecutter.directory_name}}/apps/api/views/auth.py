from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils.translation import gettext as _
from django.utils import timezone

from apps.api.errors import ValidationException, ProblemDetailException
from apps.api.forms.token import TokenForm
from apps.api.response import SingleResponse
from apps.api.views.base import SecuredView
from apps.core.models import Token
from apps.core.serializers.token import TokenSerializer


class UserAuth(SecuredView):
    EXEMPT_AUTH = ['POST']

    @transaction.atomic
    def post(self, request):
        form = TokenForm.Basic.create_from_request(request)

        if not form.is_valid():
            raise ValidationException(request, form)

        user = authenticate(request, email=form.cleaned_data['email'], password=form.cleaned_data['password'])

        if not user:
            raise ProblemDetailException(
                request,
                title=_('Incorrect email or password.'),
                status=HTTPStatus.UNAUTHORIZED,
                detail_type=ProblemDetailException.DetailType.INVALID_CREDENTIALS
            )

        token = Token.objects.create(
            user_id=user.pk,
            expires_at=timezone.now() + settings.TOKEN_EXPIRATION
        )

        return SingleResponse(request, token, status=HTTPStatus.OK, serializer=TokenSerializer.Base)


class LogoutManager(SecuredView):
    @transaction.atomic
    def delete(self, request):
        token = getattr(request, "token")

        if token:
            token.hard_delete()

        return SingleResponse(request, status=HTTPStatus.NO_CONTENT)
