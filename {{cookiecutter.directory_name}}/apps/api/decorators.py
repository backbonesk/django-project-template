from functools import wraps
from http import HTTPStatus

from django.utils.translation import gettext as _

from apps.api.errors import ApiException


def apikey_exempt(view_func):
    """
    Mark a view function as being exempt from signature and apikey check.
    """
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.apikey_exempt = True
    return wraps(view_func)(wrapped_view)


def permission_required(perm):
    """
    Mark a view function to check specific user permission.
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if request.user.has_perm(perm):
                return func(request, *args, **kwargs)
            else:
                raise ApiException(request, _('Permission denied.'), status_code=HTTPStatus.FORBIDDEN)

        return wrapper
    return decorator
