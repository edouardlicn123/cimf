# -*- coding: utf-8 -*-
"""
系统设置视图模块
"""

import json
import logging
import os

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.conf import settings as django_settings

from core.models import SystemSetting
from core.services import SettingsService, UserService, PermissionService
from core.constants import UserRole, UserTheme, Language
from core.forms import ProfileForm, PreferencesForm, ChangePasswordForm
from core.decorators import admin_required

logger = logging.getLogger(__name__)


@admin_required
def system_settings(request):
    """系统设置页面"""
    if request.method == 'POST':
        settings_dict = {}
        
        for key in SettingsService.DEFAULT_SETTINGS.keys():
            if key in ['enable_audit_log', 'enable_web_watermark', 'enable_watermark_console_detection',
                       'enable_watermark_shortcut_block', 'enable_export_watermark',
                       'cron_time_sync_enabled', 'cron_cache_cleanup_enabled', 'site_logo_enabled']:
                value = 'true' if request.POST.get(key) else 'false'
            elif key == 'web_watermark_content':
                values = request.POST.getlist(key)
                value = ','.join(values) if values else ''
            else:
                value = request.POST.get(key)
            
            if value is not None:
                settings_dict[key] = value
        
        logo_file = request.FILES.get('site_logo_upload')
        if logo_file:
            # 验证文件类型
            allowed_types = ['image/png', 'image/jpeg', 'image/gif', 'image/webp']
            if logo_file.content_type not in allowed_types:
                messages.error(request, '只允许上传图片文件（PNG/JPG/GIF/WEBP）')
                return redirect('core:system_settings')
            
            # 验证文件大小（最大 2MB）
            if logo_file.size > 2 * 1024 * 1024:
                messages.error(request, '文件大小不能超过 2MB')
                return redirect('core:system_settings')
            
            # 验证文件扩展名
            allowed_exts = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
            ext = os.path.splitext(logo_file.name)[1].lower()
            if ext not in allowed_exts:
                messages.error(request, '文件扩展名不合法')
                return redirect('core:system_settings')
            
            upload_dir = os.path.join(django_settings.MEDIA_ROOT, 'logos')
            os.makedirs(upload_dir, exist_ok=True)
            
            old_path = os.path.join(upload_dir, 'custom.png')
            if os.path.exists(old_path):
                os.remove(old_path)
            
            try:
                with open(old_path, 'wb+') as destination:
                    for chunk in logo_file.chunks():
                        destination.write(chunk)
            except Exception as e:
                messages.error(request, f'文件保存失败: {str(e)}')
                return redirect('core:system_settings')
            
            settings_dict['site_logo_path'] = 'logos/custom.png'
        
        SettingsService.save_settings_bulk(settings_dict)
        messages.success(request, '系统设置已保存')
        return redirect('core:system_settings')
    
    settings = SettingsService.get_all_settings()
    return render(request, 'admin/system_settings.html', {
        'settings': settings,
        'active_section': 'settings',
    })


@admin_required
def system_permissions(request):
    """权限管理页面"""
    if request.method == 'POST':
        manager_perms = request.POST.getlist('permissions_manager')
        PermissionService.save_role_permissions('manager', manager_perms)
        
        leader_perms = request.POST.getlist('permissions_leader')
        PermissionService.save_role_permissions('leader', leader_perms)
        
        employee_perms = request.POST.getlist('permissions_employee')
        PermissionService.save_role_permissions('employee', employee_perms)
        
        for role in ['manager', 'leader', 'employee']:
            role_name = request.POST.get(f'role_name_{role}', '').strip()
            if role_name:
                SystemSetting.objects.update_or_create(
                    key=f'role_name_{role}',
                    defaults={'value': role_name, 'description': f'{role} 角色显示名称'}
                )
        
        messages.success(request, '权限已保存')
        return redirect('core:system_permissions')
    
    role_labels = dict(UserRole.LABELS)
    for role in ['manager', 'leader', 'employee']:
        setting = SystemSetting.objects.filter(key=f'role_name_{role}').first()
        if setting and setting.value:
            role_labels[role] = setting.value
        elif not setting:
            logger.debug(f"配置未找到: role_name_{role}，使用默认值")
    
    node_perms = PermissionService.get_node_permissions()
    system_perms = PermissionService.get_system_permissions()
    roles = ['manager', 'leader', 'employee']
    role_permissions = {role: PermissionService.get_role_permissions_from_db(role) for role in roles}
    
    return render(request, 'admin/system_permissions.html', {
        'node_permissions': node_perms,
        'system_permissions': system_perms,
        'role_permissions': role_permissions,
        'role_labels': role_labels,
        'roles': roles,
        'active_section': 'permissions',
    })


@login_required
def change_password(request):
    """修改密码页面（独立页面）"""
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                new_password = form.cleaned_data.get('new_password')
                UserService.change_password(request.user.id, new_password)
                messages.success(request, '密码修改成功，请使用新密码重新登录')
                logout(request)
                return redirect('core:login')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, '表单验证失败')
    else:
        form = ChangePasswordForm(user=request.user)
    
    return render(request, 'usermenu/change_password.html', {
        'form': form,
    })


@login_required
def profile(request):
    """个人中心 - 跳转到 profile_view"""
    return redirect('core:profile_view')


@login_required
def profile_view(request):
    """个人中心 - 查看个人信息"""
    return render(request, 'usermenu/profile.html', {
        'role_labels': dict(UserRole.LABELS),
        'theme_labels': dict(UserTheme.LABELS),
        'badge_classes': dict(UserRole.BADGE_CLASSES),
    })


@login_required
def profile_settings(request):
    """用户设置页面：个人信息 + 偏好设置 + 修改密码"""
    profile_form = ProfileForm(request.POST or None, user_id=request.user.id)
    pref_form = PreferencesForm(request.POST or None)
    pwd_form = ChangePasswordForm(request.POST or None, user=request.user)
    
    if request.method == 'POST':
        if 'submit_profile' in request.POST and profile_form.is_valid():
            try:
                UserService.update_profile(
                    user_id=request.user.id,
                    nickname=profile_form.cleaned_data.get('nickname'),
                    email=profile_form.cleaned_data.get('email')
                )
                messages.success(request, '个人信息已更新成功')
            except ValueError as e:
                messages.error(request, str(e))
        
        elif 'submit_preferences' in request.POST and pref_form.is_valid():
            try:
                UserService.update_preferences(
                    user_id=request.user.id,
                    theme=pref_form.cleaned_data.get('theme'),
                    notifications_enabled=pref_form.cleaned_data.get('notifications_enabled'),
                    preferred_language=pref_form.cleaned_data.get('preferred_language')
                )
                messages.success(request, '偏好设置已保存')
            except ValueError as e:
                messages.error(request, str(e))
        
        elif 'submit_password' in request.POST and pwd_form.is_valid():
            try:
                new_password = pwd_form.cleaned_data.get('new_password')
                UserService.change_password(request.user.id, new_password)
                messages.success(request, '密码修改成功，请使用新密码重新登录')
                logout(request)
                return redirect('core:login')
            except ValueError as e:
                messages.error(request, str(e))
        
        return redirect('core:profile_settings')
    
    profile_form = ProfileForm(user_id=request.user.id, initial={
        'nickname': request.user.nickname,
        'email': request.user.email,
    })
    pref_form = PreferencesForm(initial={
        'theme': request.user.theme,
        'notifications_enabled': request.user.notifications_enabled,
        'preferred_language': request.user.preferred_language,
    })
    pwd_form = ChangePasswordForm(user=request.user)
    
    return render(request, 'usermenu/settings.html', {
        'profile_form': profile_form,
        'pref_form': pref_form,
        'pwd_form': pwd_form,
        'theme_choices': UserTheme.DISPLAY_LABELS.items(),
        'language_choices': Language.CHOICES,
    })


@login_required
def homepage_settings(request):
    """首页卡片设置"""
    from core.module.models import Module
    from importlib import import_module
    
    setting = SystemSetting.objects.filter(key='user_dashboard_card_positions').first()
    positions = {}
    if setting and setting.value:
        try:
            positions = json.loads(setting.value)
        except Exception:
            positions = {}
    elif not setting:
        logger.debug("配置未找到: user_dashboard_card_positions，使用默认值")
    
    default_positions = {str(i): {'module': None} for i in range(1, 7)}
    for k, v in positions.items():
        default_positions[k] = v
    
    available_modules = []
    
    try:
        active_modules = Module.objects.filter(is_active=True)
        for node_module in active_modules:
            module_path = node_module.path
            if module_path:
                try:
                    mod = import_module(f'modules.{module_path}.module')
                    if hasattr(mod, 'MODULE_INFO'):
                        module_info = {
                            'id': node_module.module_id,
                            'name': mod.MODULE_INFO.get('name', node_module.module_id),
                            'icon': mod.MODULE_INFO.get('icon', 'bi-grid'),
                        }
                        available_modules.append(module_info)
                except Exception:
                    pass
    except Exception:
        pass
    
    return render(request, 'usermenu/homepage_settings.html', {
        'available_modules': available_modules,
        'positions': default_positions,
    })