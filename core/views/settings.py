"""
系统设置视图模块
"""

import json
import logging
from pathlib import Path

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from core.constants import Language, UserRole, UserTheme
from core.decorators import admin_required, handle_form_errors
from core.forms import ChangePasswordForm, PreferencesForm, ProfileForm
from core.forms.admin_forms import SystemSettingsForm
from core.services import PermissionService, SettingsService, UserService
from core.utils.views import redirect_with_error, redirect_with_success

logger = logging.getLogger(__name__)

COMMON_ROLES = [role for role, _ in UserRole.CHOICES]


def _handle_logo_upload(request, settings_dict) -> HttpResponseRedirect | None:
    """处理 logo 上传，失败时返回 redirect，成功/无文件时返回 None"""
    logo_file = request.FILES.get("site_logo_upload")
    if not logo_file:
        return None

    from core.utils.response import validate_upload  # noqa: PLC0415

    valid, error_msg = validate_upload(
        logo_file,
        allowed_mimes=["image/png", "image/jpeg", "image/gif", "image/webp"],
        max_size=2 * 1024 * 1024,
        allowed_exts=[".png", ".jpg", ".jpeg", ".gif", ".webp"],
    )
    if not valid:
        return redirect_with_error(request, error_msg, "core:system_settings")

    upload_dir = Path(django_settings.MEDIA_ROOT) / "logos"
    upload_dir.mkdir(parents=True, exist_ok=True)

    old_path = upload_dir / "custom.png"
    if old_path.exists():
        old_path.unlink()

    try:
        with old_path.open("wb+") as destination:
            for chunk in logo_file.chunks():
                destination.write(chunk)
    except Exception as e:
        logger.error("Logo 文件保存失败: %s", e, exc_info=True)
        return redirect_with_error(request, "文件保存失败，请检查服务器配置", "core:system_settings")

    settings_dict["site_logo_path"] = "logos/custom.png"
    return None


@admin_required
def system_settings(request):
    """系统设置页面"""
    if request.method == "POST":
        form = SystemSettingsForm(request.POST)
        if not form.is_valid():
            return redirect_with_error(request, "表单验证失败，请检查输入", "core:system_settings")

        settings_dict = {}
        for key in SettingsService.SETTINGS_META:
            if SettingsService.SETTINGS_META[key]["type"] is bool:
                value = "true" if request.POST.get(key) else "false"
            elif key == "web_watermark_content":
                values = request.POST.getlist(key)
                value = ",".join(values) if values else ""
            else:
                value = request.POST.get(key)

            if value is not None:
                settings_dict[key] = value

        response = _handle_logo_upload(request, settings_dict)
        if response:
            return response

        SettingsService.save_settings_bulk(settings_dict)
        return redirect_with_success(request, "系统设置已保存", "core:system_settings")

    settings = SettingsService.get_all_settings()
    return render(
        request,
        "admin/system_settings.html",
        {
            "settings": settings,
        },
    )


@admin_required
def system_permissions(request):
    """权限管理页面"""
    if request.method == "POST":
        manager_perms = request.POST.getlist("permissions_manager")
        PermissionService.save_role_permissions("manager", manager_perms)

        leader_perms = request.POST.getlist("permissions_leader")
        PermissionService.save_role_permissions("leader", leader_perms)

        employee_perms = request.POST.getlist("permissions_employee")
        PermissionService.save_role_permissions("employee", employee_perms)

        for role in COMMON_ROLES:
            role_name = request.POST.get(f"role_name_{role}", "").strip()
            if role_name:
                SettingsService.update_setting(f"role_name_{role}", role_name)

        return redirect_with_success(request, "权限已保存", "core:system_permissions")

    role_labels = dict(UserRole.LABELS)
    for role in COMMON_ROLES:
        role_label = SettingsService.get_setting(f"role_name_{role}")
        if role_label:
            role_labels[role] = role_label
        elif role_label is None:
            logger.debug("配置未找到: role_name_%s，使用默认值", role)

    node_perms = PermissionService.get_node_permissions()
    system_perms = PermissionService.get_system_permissions()
    roles = COMMON_ROLES
    role_permissions = {role: PermissionService.get_role_permissions_from_db(role) for role in roles}

    return render(
        request,
        "admin/system_permissions.html",
        {
            "node_permissions": node_perms,
            "system_permissions": system_perms,
            "role_permissions": role_permissions,
            "role_labels": role_labels,
            "roles": roles,
        },
    )


def _handle_password_change(user_id: int, new_password: str, request) -> HttpResponseRedirect:
    """执行密码修改并登出重定向到登录页"""
    UserService.change_password(user_id, new_password)
    logout(request)
    return redirect_with_success(request, "密码修改成功，请使用新密码重新登录", "core:login")


@login_required
def change_password(request):
    """修改密码页面（独立页面）"""
    if request.method == "POST":
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            return _handle_password_change(request.user.id, form.cleaned_data.get("new_password"), request)
        messages.error(request, "表单验证失败")
    else:
        form = ChangePasswordForm(user=request.user)

    return render(
        request,
        "usermenu/change_password.html",
        {
            "form": form,
        },
    )


@login_required
def profile_view(request):
    """个人中心 - 查看个人信息"""
    return render(
        request,
        "usermenu/profile.html",
        {
            "role_labels": dict(UserRole.LABELS),
            "theme_labels": dict(UserTheme.LABELS),
            "badge_classes": dict(UserRole.BADGE_CLASSES),
        },
    )


def _handle_profile_post(request, form) -> HttpResponseRedirect | None:
    if form.is_valid():
        UserService.update_profile(
            user_id=request.user.id,
            nickname=form.cleaned_data.get("nickname"),
            email=form.cleaned_data.get("email"),
        )
        return redirect_with_success(request, "个人信息已更新成功", "core:profile_settings")
    messages.error(request, "请检查个人信息表单中的错误")
    return None


def _handle_preferences_post(request, form) -> HttpResponseRedirect | None:
    if form.is_valid():
        UserService.update_preferences(
            user_id=request.user.id,
            theme=form.cleaned_data.get("theme"),
            notifications_enabled=form.cleaned_data.get("notifications_enabled"),
            preferred_language=form.cleaned_data.get("preferred_language"),
        )
        return redirect_with_success(request, "偏好设置已保存", "core:profile_settings")
    messages.error(request, "请检查偏好设置表单中的错误")
    return None


def _handle_password_post(request, form) -> HttpResponseRedirect | None:
    if form.is_valid():
        return _handle_password_change(request.user.id, form.cleaned_data.get("new_password"), request)
    messages.error(request, "请检查密码表单中的错误")
    return None


def _build_initial_profile(user):
    return ProfileForm(user_id=user.id, initial={"nickname": user.nickname, "email": user.email})


def _build_initial_preferences(user):
    return PreferencesForm(
        initial={
            "theme": user.theme,
            "notifications_enabled": user.notifications_enabled,
            "preferred_language": user.preferred_language,
        }
    )


@login_required
@handle_form_errors
def profile_settings(request):
    """用户设置页面：个人信息 + 偏好设置 + 修改密码"""
    if request.method == "POST":
        handlers = {
            "submit_profile": lambda: _handle_profile_post(request, ProfileForm(request.POST, user_id=request.user.id)),
            "submit_preferences": lambda: _handle_preferences_post(request, PreferencesForm(request.POST)),
            "submit_password": lambda: _handle_password_post(request, ChangePasswordForm(request.POST, user=request.user)),
        }
        for key, handler in handlers.items():
            if key in request.POST:
                return handler()
        return redirect("core:profile_settings")

    return render(
        request,
        "usermenu/settings.html",
        {
            "profile_form": _build_initial_profile(request.user),
            "pref_form": _build_initial_preferences(request.user),
            "pwd_form": ChangePasswordForm(user=request.user),
            "theme_choices": UserTheme.DISPLAY_LABELS.items(),
            "language_choices": Language.CHOICES,
        },
    )


@login_required
def homepage_settings(request):
    """首页卡片设置"""
    from core.module.services.module_service import ModuleService  # noqa: PLC0415

    positions_str = SettingsService.get_setting("user_dashboard_card_positions")
    positions = {}
    if positions_str:
        try:
            positions = json.loads(positions_str)
        except Exception as e:
            logger.warning("解析卡片位置配置失败: %s", e, exc_info=True)
            positions = {}
    elif positions_str is None:
        logger.debug("配置未找到: user_dashboard_card_positions，使用默认值")

    default_positions = {str(i): {"module": None} for i in range(1, 7)} | positions

    available_modules = ModuleService.get_frontpage_modules()

    return render(
        request,
        "usermenu/homepage_settings.html",
        {
            "available_modules": available_modules,
            "positions": default_positions,
        },
    )
