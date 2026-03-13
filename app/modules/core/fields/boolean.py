from .base import BaseField

class BooleanField(BaseField):
    name = 'boolean'
    label = '布尔值'
    widget = 'checkbox'
    properties = ['value']
    
    def render(self, value, mode='edit'):
        checked = 'checked' if value.get('value') else ''
        if mode == 'view':
            return '是' if value.get('value') else '否'
        return f'<input type="checkbox" name="{self.field_name}" value="1" {checked}>'
    
    def validate(self, value):
        return []
    
    def format(self, value):
        return '是' if value.get('value') else '否'
