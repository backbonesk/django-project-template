import hashlib
import hmac
from http import HTTPStatus
from typing import Dict, Union
from sentry_sdk import set_tag

from django.conf import settings
from django.contrib.auth import load_backend
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.utils.translation import gettext as _
from django.views import View

from apps.api.errors import ProblemDetailException
from apps.core.models import ApiKey
from apps.api.errors import UnauthorizedException


class SecuredView(View):
    EXEMPT_AUTH = []
    EXEMPT_API_KEY = []
    REQUIRE_SUPERUSER = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._backends: Dict[str, BaseBackend] = {}
        for schema, backend in settings.SECURED_VIEW_AUTHENTICATION_SCHEMAS.items():
            self._backends[schema.lower()] = load_backend(backend)

    def _authenticate(self, request) -> Union[AnonymousUser, AbstractBaseUser]:
        if request.method in self.EXEMPT_AUTH:
            return AnonymousUser()

        auth_header = request.headers.get('Authorization', '')
        if not auth_header:
            return AnonymousUser()

        auth_header = str(auth_header).split(' ')

        if len(auth_header) != 2:
            raise UnauthorizedException(request, detail=_("Invalid or missing Authorization header"))

        if not auth_header[0] in settings.SECURED_VIEW_AUTHENTICATION_SCHEMAS.keys():
            raise UnauthorizedException(request, detail=_('Unsupported authentication schema'))

        auth_params = {
            auth_header[0].lower(): auth_header[1]
        }

        return self._backends[auth_header[0].lower()].authenticate(request, **auth_params)

    def _check_api_key(self, request):
        api_key = request.headers.get('X-Apikey')

        try:
            api_key_model = ApiKey.objects.get(pk=api_key, is_active=True)
        except ApiKey.DoesNotExist:
            raise ProblemDetailException(
                request, _('Invalid api key.'), status=HTTPStatus.UNAUTHORIZED,
                detail_type=ProblemDetailException.DetailType.INVALID_APIKEY
            )

        request.api_key = api_key_model
        set_tag('apikey.platform', request.api_key.platform)

        if api_key_model.platform == ApiKey.DevicePlatform.DEBUG and not settings.DEBUG:
            raise ProblemDetailException(
                request,
                title=_('Invalid api key.'),
                status=HTTPStatus.UNAUTHORIZED,
                detail_type=ProblemDetailException.DetailType.INVALID_APIKEY
            )
        else:
            self._check_signature(request, api_key_model)

        return None

    @staticmethod
    def _check_signature(request: HttpRequest, api_key: ApiKey):
        signature = request.headers.get('X-Signature', '')

        # Do not check signature for DEBUG API keys and DEBUG environment
        if api_key.platform == ApiKey.DevicePlatform.DEBUG or settings.DEBUG:
            return None

        message = f"{request.body.decode('utf-8')}:{request.path}"
        signature_check = hmac.new(
            api_key.secret.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        if signature != signature_check:
            raise ProblemDetailException(
                request,
                _('Invalid signature.'),
                status=HTTPStatus.BAD_REQUEST,
                to_sentry=True,
                additional_data={
                    'received': signature,
                    'expected': signature_check,
                    'message': message,
                },
                detail_type=ProblemDetailException.DetailType.INVALID_SIGNATURE
            )

        return None

    def dispatch(self, request, *args, **kwargs):
        if request.method not in self.EXEMPT_API_KEY:
            self._check_api_key(request)

        request.user = self._authenticate(request)
        if not settings.IS_ENABLED_ANONYMOUS_USER:
            if request.user.is_anonymous:
                raise ProblemDetailException(
                    request,
                    title=_('Invalid or missing Authorization header.'),
                    status=HTTPStatus.UNAUTHORIZED,
                    detail_type=ProblemDetailException.DetailType.INVALID_TOKEN,
                    extra_headers=(
                        ('WWW-Authenticate', f'Bearer realm="{settings.INSTANCE_NAME}'),
                    )
                )

        if request.method in self.REQUIRE_SUPERUSER:
            if not request.user.is_superuser:
                raise ProblemDetailException(
                    request, _('Insufficient permissions'), status=HTTPStatus.FORBIDDEN,
                )

        return super().dispatch(request, *args, **kwargs)
