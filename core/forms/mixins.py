"""
表单混合类，统一 Bootstrap 样式
"""

from django import forms

from core.forms.validators import validate_unique_email


class BootstrapFormMixin:
    """
    自动为表单字段添加 Bootstrap class

    用法：
    class MyForm(BootstrapFormMixin, forms.ModelForm):
        large = True  # 使用 large 尺寸
        pass
    """

    large = True  # 是否使用 large 尺寸

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        size_class = "form-control-lg" if self.large else ""
        select_size = "form-select-lg" if self.large else ""

        for field in self.fields.values():
            # 跳过已手动指定 class 的字段
            if "class" in field.widget.attrs:
                continue

            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs["class"] = f"form-control {size_class}".strip()
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs["class"] = "form-control"
            elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs["class"] = f"form-select {select_size}".strip()
            elif isinstance(field.widget, (forms.PasswordInput, forms.EmailInput, forms.NumberInput)):
                field.widget.attrs["class"] = f"form-control {size_class}".strip()
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"


class UserAwareFormMixin:
    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop("user_id", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)


class EmailCleanMixin:
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            email = email.strip()
            validate_unique_email(email, exclude_user_id=getattr(self, "user_id", None))
        return email


class UsernameCleanMixin:
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            username = username.strip()
            return username
        return username


_USER_FORM_WIDGETS = {
    "username": forms.TextInput(
        attrs={
            "placeholder": "用于登录的唯一账号（3-64 字符）",
            "autocomplete": "username",
        }
    ),
    "nickname": forms.TextInput(
        attrs={
            "placeholder": "仪表盘、项目成员列表等处显示的友好名称",
            "autocomplete": "name",
        }
    ),
    "email": forms.EmailInput(
        attrs={
            "placeholder": "用于密码重置、系统通知（可留空）",
            "autocomplete": "email",
        }
    ),
    "is_admin": forms.CheckboxInput(attrs={"role": "switch"}),
}
