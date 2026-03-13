from .base import BaseField

class IntegerField(BaseField):
    name = 'integer'
    label = '整数'
    widget = 'input'
    properties = ['value']
    
    def render(self, value, mode='edit'):
        if mode == 'view':
            return str(value.get('value', ''))
        return f'<input type="number" name="{self.field_name}" value="{value.get("value", "")}" class="form-control">'
    
    def validate(self, value):
        errors = []
        val = value.get('value')
        if self.field_config.get('required') and not val:
            errors.append(f'{self.field_config.get("label")} 为必填项')
        if val and not str(val).isdigit():
            errors.append(f'{self.field_config.get("label")} 必须为整数')
        return errors
