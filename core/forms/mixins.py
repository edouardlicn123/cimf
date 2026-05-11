"""
表单混合类，统一 Bootstrap 样式
"""

from django import forms


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

        size_class = 'form-control-lg' if self.large else ''
        select_size = 'form-select-lg' if self.large else ''

        for field in self.fields.values():
            # 跳过已手动指定 class 的字段
            if 'class' in field.widget.attrs:
                continue

            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs['class'] = f'form-control {size_class}'.strip()
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = f'form-select {select_size}'.strip()
            elif isinstance(field.widget, (forms.PasswordInput, forms.EmailInput, forms.NumberInput)):
                field.widget.attrs['class'] = f'form-control {size_class}'.strip()
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
