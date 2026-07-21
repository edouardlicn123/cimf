"""
认证视图模块
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from core.forms import LoginForm
from core.services import AuthService, SettingsService


def login_view(request):
    """用户登录页面

    GET: 显示登录表单
    POST: 处理登录请求
    """
    if request.user.is_authenticated:
        messages.info(request, "您已登录，无需重复登录")
        return redirect("core:dashboard")

    error_message = None
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request.POST)
        if not form.is_valid():
            error_message = "用户名或密码格式不正确"
        else:
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            result = AuthService.login(username, password)

            if result["success"]:
                user = result["user"]
                login(request, user)
                request.session.cycle_key()
                next_url = request.GET.get("next")
                if next_url and url_has_allowed_host_and_scheme(next_url, request.get_host()):
                    return redirect(next_url)
                return redirect("core:dashboard")
            else:
                error_message = result["message"]

    form = form if request.method == "POST" else LoginForm()
    return render(
        request,
        "auth/login.html",
        {
            "form": form,
            "error_message": error_message,
            "settings": SettingsService.get_all_settings(),
        },
    )


@login_required
@require_POST
def logout_view(request):
    """用户登出"""
    logout(request)
    messages.info(request, "您已安全退出登录")
    return redirect("core:login")
