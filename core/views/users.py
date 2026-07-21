"""用户管理视图模块"""

import logging

from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from core.decorators import admin_required
from core.forms.admin_forms import UserCreateForm, UserEditForm
from core.models import User
from core.services import UserService
from core.utils.views import redirect_with_error, redirect_with_success

logger = logging.getLogger(__name__)


@admin_required
def system_users(request):
    """系统用户列表"""
    search_term = request.GET.get("search", "")
    only_active = request.GET.get("only_active", "true") == "true"
    role_filter = request.GET.get("role_filter", "")

    users = UserService.get_user_list(
        search_term=search_term or None,
        only_active=only_active,
        exclude_admin=True,
        role=role_filter or None,
    )

    return render(
        request,
        "admin/system_users.html",
        {
            "users": users,
            "search_term": search_term,
            "only_active": only_active,
            "role_filter": role_filter,
            "active_section": "users",
        },
    )


@admin_required
def user_create(request):
    """创建用户"""
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            try:
                UserService.create_user(
                    username=form.cleaned_data["username"],
                    nickname=form.cleaned_data["nickname"] or form.cleaned_data["username"],
                    email=form.cleaned_data["email"] or None,
                    password=form.cleaned_data["password"],
                    role=form.cleaned_data["role"],
                    is_admin=form.cleaned_data["is_admin"],
                )
                return redirect_with_success(request, "用户创建成功", "core:system_users")
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = UserCreateForm()

    return render(
        request,
        "admin/system_user_edit.html",
        {
            "form": form,
            "is_create": True,
        },
    )


@admin_required
def user_edit(request, user_id: int):
    """编辑用户"""
    user = get_object_or_404(User, id=user_id)

    if user_id == 1:
        return redirect_with_error(request, "系统管理员账号禁止编辑", "core:system_users")

    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user, user_id=user_id)
        if form.is_valid():
            try:
                UserService.update_user(
                    user_id=user_id,
                    username=form.cleaned_data["username"],
                    nickname=form.cleaned_data["nickname"],
                    email=form.cleaned_data["email"] or None,
                    password=form.cleaned_data["password"] if form.cleaned_data["password"] else None,
                    role=form.cleaned_data["role"],
                    is_admin=form.cleaned_data["is_admin"],
                    is_active=form.cleaned_data["is_active"],
                )
                return redirect_with_success(request, "用户信息更新成功", "core:system_users")
            except (ValueError, PermissionError) as e:
                messages.error(request, str(e))
    else:
        form = UserEditForm(instance=user, user_id=user_id)

    return render(
        request,
        "admin/system_user_edit.html",
        {
            "form": form,
            "user": user,
            "is_create": False,
        },
    )


@admin_required
@require_POST
def user_delete(request, user_id: int):
    """删除用户"""
    if user_id == 1:
        return redirect_with_error(request, "系统管理员账号禁止删除", "core:system_users")

    if user_id == request.user.id:
        return redirect_with_error(request, "禁止删除当前登录账号", "core:system_users")

    user = get_object_or_404(User, id=user_id)
    try:
        user.delete()
        return redirect_with_success(request, "用户已删除", "core:system_users")
    except ProtectedError:
        return redirect_with_error(request, "该用户有关联数据，无法删除", "core:system_users")
    except Exception as e:
        logger.error("删除用户失败: user_id=%d, error=%s", user_id, e, exc_info=True)
        return redirect_with_error(request, "删除用户失败", "core:system_users")
