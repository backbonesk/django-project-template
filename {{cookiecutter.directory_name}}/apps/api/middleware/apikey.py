import hashlib
import hmac
from http import HTTPStatus

from django.conf import settings
from django.utils.translation import gettext as _

from apps.api.errors import ApiException
from apps.api.response import ErrorResponse
from apps.core.models import ApiKey


class ApiKeyMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        # View functions
        if hasattr(view_func, 'apikey_exempt'):
            if view_func.apikey_exempt:
                return None

        # View classes
        if hasattr(view_func, 'view_class'):
            if hasattr(view_func.view_class, 'apikey_exempt'):
                if request.method.lower() in [item.lower() for item in view_func.view_class.apikey_exempt]:
                    return None

        api_key = request.headers.get('X-Apikey')
        signature = request.headers.get('X-Signature', '')
        try:
            api_key_model = ApiKey.objects.get(pk=api_key, is_active=True)
        except ApiKey.DoesNotExist:
            return ErrorResponse.create_from_exception(ApiException(request, _('Invalid api key.')))

        request.api_key = api_key_model

        # Do not check signature for GitLab API keys
        if api_key_model.platform == ApiKey.DevicePlatform.GILTAB:
            return None

        message = f"{request.body.decode('utf-8')}:{request.path}"
        signature_check = hmac.new(
            api_key_model.secret.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        # Do not check signature for DEBUG API keys in DEBUG environment
        if api_key_model.platform == ApiKey.DevicePlatform.DEBUG and settings.DEBUG:
            return None

        if signature != signature_check:
            return ErrorResponse.create_from_exception(
                ApiException(
                    request,
                    _('Invalid signature.'),
                    HTTPStatus.FORBIDDEN,
                    to_sentry=True,
                    additional_data={
                        'received': signature,
                        'expected': signature_check,
                        'message': message,
                    }
                )
            )
        return None


__all__ = [
    'ApiKeyMiddleware'
]
