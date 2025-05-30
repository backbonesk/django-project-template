from http import HTTPStatus

from django.conf import settings
from django.core.exceptions import RequestDataTooBig
from django.utils.translation import gettext as _

from apps.api.errors import ProblemDetailException, ValidationException, ProblemDetail, DetailType
from apps.api.response import ErrorResponse, ValidationResponse


class ExceptionMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    @staticmethod
    def process_exception(request, exception):
        if isinstance(exception, ProblemDetailException):
            return ErrorResponse(request, exception.payload, status=exception.status, headers=exception.extra_headers)
        if isinstance(exception, ValidationException):
            return ValidationResponse(request, exception.payload, status=exception.status)
        if isinstance(exception, RequestDataTooBig):
            return ErrorResponse(
                request=request,
                payload=ProblemDetail(
                    title=_('Request payload too big!'),
                    type=DetailType.REQUEST_PAYLOAD_TOO_BIG,
                    detail=f'max_payload: {settings.DATA_UPLOAD_MAX_MEMORY_SIZE}'
                ),
                status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE
            )


__all__ = [
    'ExceptionMiddleware'
]
