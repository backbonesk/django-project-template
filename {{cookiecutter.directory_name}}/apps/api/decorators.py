from functools import wraps


def apikey_exempt(view_func):
    """
    Mark a view function as being exempt from signature and apikey check.
    """
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    wrapped_view.apikey_exempt = True
    return wraps(view_func)(wrapped_view)
