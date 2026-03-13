from .base import BaseField

class FloatField(BaseField):
    name = 'float'
    label = '浮点数'
    widget = 'input'
    properties = ['value']
    
    def render(self, value, mode='edit'):
        if mode == 'view':
            return str(value.get('value', ''))
        return f'<input type="number" step="any" name="{self.field_name}" value="{value.get("value", "")}" class="form-control">'
    
    def validate(self, value):
        errors = []
        val = value.get('value')
        if self.field_config.get('required') and not val:
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
