from .base import BaseField

class EmailField(BaseField):
    name = 'email'
    label = '邮箱'
    widget = 'input'
    properties = ['value']
    
    def render(self, value, mode='edit'):
        if mode == 'view':
            return value.get('value', '')
        return f'<input type="email" name="{self.field_name}" value="{value.get("value", "")}" class="form-control">'
    
    def validate(self, value):
        import re
        errors = []
        email = value.get('value', '')
        if self.field_config.get('required') and not email:
            errors.append(f'{self.field_config.get("label")} 为必填项')
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            errors.append(f'{self.field_config.get("label")} 格式不正确')
        return errors
