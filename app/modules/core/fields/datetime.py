from .base import BaseField
from datetime import datetime

class DatetimeField(BaseField):
    name = 'datetime'
    label = '日期时间'
    widget = 'datetime_input'
    properties = ['value']
    
    def render(self, value, mode='edit'):
        val = value.get('value', '')
        if mode == 'view':
            if val:
                try:
                    dt = datetime.fromisoformat(val.replace('Z', '+00:00'))
                    return dt.strftime('%Y-%m-%d %H:%M')
                except:
                    return val
            return ''
        
        return f'<input type="datetime-local" name="{self.field_name}" value="{val}" class="form-control">'
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
