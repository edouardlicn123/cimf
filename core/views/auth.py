"""
认证视图模块
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from core.services import AuthService, SettingsService


def login_view(request):
    """用户登录页面

    GET: 显示登录表单
    POST: 处理登录请求
    """
    if request.user.is_authenticated:
        messages.info(request, '您已登录，无需重复登录')
        return redirect('core:dashboard')

    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        result = AuthService.login(request, username, password)

        if result['success']:
            user = result['user']
            login(request, user)
            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, request.get_host()):
                return redirect(next_url)
            return redirect('core:dashboard')
        else:
            error_message = result['message']

    return render(request, 'auth/login.html', {
        'error_message': error_message,
        'settings': SettingsService.get_all_settings(),
    })


def logout_view(request):
    """用户登出"""
    logout(request)
    messages.info(request, '您已安全退出登录')
    return redirect('core:login')
