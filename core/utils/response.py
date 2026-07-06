from django.http import JsonResponse


def json_success(data=None, message=None, status=200, extra=None):
    resp = {"success": True}
    if data is not None:
        resp["data"] = data
    if message is not None:
        resp["message"] = message
    if extra is not None:
        resp.update(extra)
    return JsonResponse(resp, status=status)


def json_error(message, status=400, data=None):
    resp = {"success": False, "error": message}
    if data is not None:
        resp["data"] = data
    return JsonResponse(resp, status=status)


def no_cache_json_response(data, status=200):
    response = JsonResponse(data, status=status)
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response
