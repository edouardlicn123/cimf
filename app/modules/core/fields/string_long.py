from .base import BaseField

class StringLongField(BaseField):
    name = 'string_long'
    label = '多行纯文本'
    widget = 'textarea'
    properties = ['value']
    
    def render(self, value, mode='edit'):
        if mode == 'view':
            return value.get('value', '')
        return f'<textarea name="{self.field_name}" class="form-control" rows="4">{value.get("value", "")}</textarea>'
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
