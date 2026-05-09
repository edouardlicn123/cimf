# -*- coding: utf-8 -*-
"""
仪表盘视图模块
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.decorators import admin_required
from core.services import SettingsService, UserService


@login_required
def dashboard(request):
    """仪表盘"""
    stats = UserService.get_user_stats()
    settings = SettingsService.get_all_settings()
    user_display_name = request.user.nickname or request.user.username
    settings['welcome_subtitle'] = settings.get('welcome_subtitle') or '让我们一起把项目完善吧。'
    settings['welcome_intro'] = settings.get('welcome_intro') or '初始用户名：admin 初始密码：admin123'
    
    return render(request, 'indexdashboard.html', {
        'stats': stats,
        'settings': settings,
        'user_display_name': user_display_name,
        'page_title': user_display_name,
        'show_header': 'False',
    })


@admin_required
def admin_dashboard(request):
    """管理后台仪表盘"""
    stats = UserService.get_user_stats()
    from core.models import SystemSetting, Taxonomy
    
    settings_count = SystemSetting.objects.count()
    taxonomy_count = Taxonomy.objects.count()
    
    return render(request, 'admin/dashboard.html', {
        'stats': stats,
        'settings_count': settings_count,
        'taxonomy_count': taxonomy_count,
    })