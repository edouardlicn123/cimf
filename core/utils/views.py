from django.contrib import messages
from django.shortcuts import redirect


def redirect_with_message(url_name, message, level="success", *args, **kwargs):
    request = kwargs.pop("request", None)
    if request:
        getattr(messages, level)(request, message)
    return redirect(url_name, *args, **kwargs)


def redirect_with_error(request, message, url_name, *args, **kwargs):
    messages.error(request, message)
    return redirect(url_name, *args, **kwargs)


def redirect_with_success(request, message, url_name, *args, **kwargs):
    messages.success(request, message)
    return redirect(url_name, *args, **kwargs)
