from .base import BaseField

class LinkField(BaseField):
    name = 'link'
    label = '链接'
    widget = 'link_input'
    properties = ['uri', 'title', 'options']
    
    def render(self, value, mode='edit'):
        uri = value.get('uri', '')
        title = value.get('title', '')
        
        if mode == 'view':
            if uri:
                return f'<a href="{uri}" target="_blank">{title or uri}</a>'
            return ''
        
        return f'''
        <div class="link-input">
            <input type="text" name="{self.field_name}_uri" placeholder="URL" value="{uri}" class="form-control mb-2">
            <input type="text" name="{self.field_name}_title" placeholder="链接文字" value="{title}" class="form-control">
        </div>
        '''
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('uri'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
