from .base import BaseField

class TextField(BaseField):
    name = 'text'
    label = '带格式文本'
    widget = 'rich_text'
    properties = ['value', 'format']
    
    def render(self, value, mode='edit'):
        if mode == 'view':
            return value.get('value', '')
        return f'<div class="rich-text-editor" data-field="{self.field_name}"><textarea name="{self.field_name}" class="form-control rich-text">{value.get("value", "")}</textarea></div>'
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
