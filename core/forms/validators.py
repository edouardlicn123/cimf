"""
共享表单验证器
"""

from django import forms

from core.models import User


def validate_unique_email(email: str, exclude_user_id: int | None = None) -> str:
    """验证邮箱唯一性"""
    if not email:
        return email
    qs = User.objects.filter(email=email)
    if exclude_user_id:
        qs = qs.exclude(id=exclude_user_id)
    if qs.exists():
        raise forms.ValidationError("该邮箱已被其他用户使用")
    return email


def validate_unique_username(username: str, exclude_user_id: int | None = None) -> str:
    """验证用户名唯一性"""
    if not username:
        return username
    qs = User.objects.filter(username=username)
    if exclude_user_id:
        qs = qs.exclude(id=exclude_user_id)
    if qs.exists():
        raise forms.ValidationError("该用户名已被占用，请更换其他用户名")
    return username


def validate_password_confirmation(password: str, confirm_password: str) -> None:
    """验证两次密码输入是否一致"""
    if password:
        if not confirm_password:
            raise forms.ValidationError("请确认密码")
        if password != confirm_password:
            raise forms.ValidationError("两次输入的密码不一致")
        if len(password) < 10:
            raise forms.ValidationError("密码长度至少 10 个字符（建议 12+ 字符）")
