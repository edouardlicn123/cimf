from .base import BaseField

class StringField(BaseField):
    name = 'string'
    label = '单行文本'
    widget = 'input'
    properties = ['value']
    
    def render(self, value, mode='edit'):
        if mode == 'view':
            return value.get('value', '')
        return f'<input type="text" name="{self.field_name}" value="{value.get("value", "")}" class="form-control">'
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
