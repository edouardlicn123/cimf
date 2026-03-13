from .base import BaseField

class TimestampField(BaseField):
    name = 'timestamp'
    label = '时间戳'
    widget = 'datetime_input'
    properties = ['value']
    
    def render(self, value, mode='edit'):
        val = value.get('value', '')
        if mode == 'view':
            if val:
                from datetime import datetime
                try:
                    dt = datetime.fromtimestamp(int(val))
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    return val
            return ''
        
        display_val = ''
        if val:
            from datetime import datetime
            try:
                dt = datetime.fromtimestamp(int(val))
                display_val = dt.strftime('%Y-%m-%dT%H:%M:%S')
            except:
                pass
        
        return f'<input type="datetime-local" name="{self.field_name}" value="{display_val}" class="form-control">'
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
