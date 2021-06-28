import hashlib
import hmac
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpRequest
from django.utils.translation import gettext as _
from django.views import View

from apps.api.errors import ProblemDetailException
from apps.core.models import ApiKey


class SecuredView(View):
    EXEMPT_AUTH = []
    EXEMPT_API_KEY = []

    @staticmethod
    def _authenticate(request: HttpRequest):
        auth_header = request.headers.get('Authorization', '').split(' ')
        if len(auth_header) != 2:
            raise ProblemDetailException(
                request, _('Invalid or missing Authorization header'), status=HTTPStatus.UNAUTHORIZED,
                extra_headers=(
                    ('WWW-Authenticate', 'Bearer realm="pulsatio-api'),
                )
            )

        if auth_header[0] == 'Bearer':
            auth_params = {
                auth_header[0].lower(): auth_header[1]
            }
        else:
            raise ProblemDetailException(
                request,
                _('Unauthorized'),
                status=HTTPStatus.UNAUTHORIZED,
                extra_headers=(
                    ('WWW-Authenticate', 'Bearer realm="pulsatio-api'),
                )
            )

        request.user = authenticate(request, **auth_params)

    def _check_api_key(self, request):
        api_key = request.headers.get('X-Apikey')

        try:
            api_key_model = ApiKey.objects.get(pk=api_key, is_active=True)
        except ApiKey.DoesNotExist:
            raise ProblemDetailException(
                request, _('Invalid api key.'), status=HTTPStatus.UNAUTHORIZED
            )

        request.api_key = api_key_model
        self._check_signature(request, api_key_model)

        return None

    @staticmethod
    def _check_signature(request: HttpRequest, api_key: ApiKey):
        signature = request.headers.get('X-Signature', '')

        # Do not check signature for GitLab API keys, DEBUG API keys and DEBUG environment
        if api_key.platform in [ApiKey.DevicePlatform.GILTAB, ApiKey.DevicePlatform.DEBUG] or settings.DEBUG:
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
                status=HTTPStatus.UNAUTHORIZED,
                to_sentry=True,
                additional_data={
                    'received': signature,
                    'expected': signature_check,
                    'message': message,
                }
            )

        return None

    def dispatch(self, request, *args, **kwargs):
        if request.method not in self.EXEMPT_API_KEY:
            self._check_api_key(request)

        if request.method not in self.EXEMPT_AUTH:
            self._authenticate(request)

        return super().dispatch(request, *args, **kwargs)
