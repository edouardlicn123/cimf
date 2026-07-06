"""
错误处理视图模块
"""

from django.shortcuts import render


def _error_response(request, template_name, code, title, message, icon):
    return render(
        request,
        template_name,
        {
            "error_code": code,
            "error_title": title,
            "error_message": message,
            "error_icon": icon,
        },
        status=code,
    )


def error_400(request, exception):  # noqa: ARG001
    return _error_response(
        request,
        "errors/400.html",
        400,
        "无效请求",
        "服务器无法理解您的请求，可能是因为请求格式错误、缺少必要参数或数据无效。",
        "bi-exclamation-circle",
    )


def error_403(request, exception):  # noqa: ARG001
    return _error_response(
        request,
        "errors/403.html",
        403,
        "禁止访问",
        "您没有权限访问此页面。如需访问，请联系管理员获取相应权限。",
        "bi-lock",
    )


def error_404(request, exception):  # noqa: ARG001
    return _error_response(
        request,
        "errors/404.html",
        404,
        "页面未找到",
        "您访问的页面可能已被移动、删除，或者您输入的地址有误。",
        "bi-search",
    )


def error_500(request):
    return _error_response(
        request,
        "errors/500.html",
        500,
        "服务器内部错误",
        "很抱歉，系统在处理您的请求时遇到了意外问题。我们已经记录了这个错误，并正在努力修复。",
        "bi-gear",
    )
