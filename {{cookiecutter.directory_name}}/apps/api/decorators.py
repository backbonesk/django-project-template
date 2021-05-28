from functools import wraps


def require_apikey(view_func):
    """
    Require valid signature for specified endpoint
    :param view_func:
    :return:
    """
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    wrapped_view.require_apikey = True
    return wraps(view_func)(wrapped_view)


def signature_exempt(view_func):
    """
    Mark a view function as being exempt from signature and apikey check.
    """
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    wrapped_view.signature_exempt = True
    return wraps(view_func)(wrapped_view)
