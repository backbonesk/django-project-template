from http import HTTPStatus

from django.utils.translation import gettext as _

from apps.api.errors import ProblemDetailException


def permission_required(perm):
    """
    Mark a view function to check specific user permission.
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if request.user.has_perm(perm):
                return func(request, *args, **kwargs)
            else:
                raise ProblemDetailException(request, title=_('Permission denied.'), status_code=HTTPStatus.FORBIDDEN)

        return wrapper
    return decorator
