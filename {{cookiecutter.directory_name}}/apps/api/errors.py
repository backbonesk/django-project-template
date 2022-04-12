import traceback
from enum import Enum
from http import HTTPStatus
from typing import Tuple, Optional

import sentry_sdk
from django.conf import settings
from django.forms import BaseForm
from django.utils.text import slugify
from django.utils.translation import gettext as _


class ProblemDetailException(Exception):
    class DetailType(Enum):
        INVALID_APIKEY = 'invalid-apikey'
        INVALID_SIGNATURE = 'invalid-signature'
        INVALID_CREDENTIALS = 'invalid-credentials'
        INVALID_TOKEN = 'invalid-token'

    def __init__(
        self,
        request,
        title: str,
        status: Optional[int] = HTTPStatus.INTERNAL_SERVER_ERROR,
        previous: Optional[Exception] = None,
        to_sentry: Optional[bool] = False,
        additional_data: Optional[dict] = None,
        detail_type: Optional[DetailType] = None,
        detail: Optional[str] = None,
        extra_headers: Optional[Tuple[Tuple]] = None
    ):
        super().__init__(title)

        self._request = request
        self._title = title
        self._status_code = status
        self._previous = previous
        self._type = detail_type
        self._detail = detail
        self._extra_headers = extra_headers

        if additional_data:
            self._additional_data = additional_data
        else:
            self._additional_data = {}

        if to_sentry:
            with sentry_sdk.push_scope() as scope:
                for key, value in self.__dict__.items():
                    scope.set_extra(key, value)
                sentry_sdk.capture_exception(self)

    @property
    def request(self):
        return self._request

    @property
    def title(self) -> str:
        return self._title

    @property
    def status(self) -> int:
        return self._status_code

    @property
    def previous(self) -> Exception:
        return self._previous

    @property
    def type(self) -> str:
        return self._type

    @property
    def detail(self) -> str:
        return self._detail

    @property
    def extra_headers(self) -> Tuple[Tuple]:
        return self._extra_headers

    @property
    def payload(self) -> dict:
        result = {
            'title': self.title
        }

        if settings.DEBUG:
            result['trace'] = traceback.format_exc().split('\n')

        return result


class ValidationException(ProblemDetailException):
    def __init__(self, request, form: BaseForm):
        super().__init__(request, _('Validation error!'), status=HTTPStatus.UNPROCESSABLE_ENTITY)
        self._form = form

    @property
    def payload(self) -> dict:
        payload = super(ValidationException, self).payload
        payload['validation_errors'] = self._form.errors
        return payload


class UnauthorizedException(ProblemDetailException):
    def __init__(self, request, detail: Optional[str] = None):
        super().__init__(
            request,
            _("Unauthorized"),
            status=HTTPStatus.UNAUTHORIZED,
            extra_headers=(
                ('WWW-Authenticate', f'Bearer realm="{slugify(settings.INSTANCE_NAME)}"'),
            ),
            detail=detail
        )
