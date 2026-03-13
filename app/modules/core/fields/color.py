from .base import BaseField

class ColorField(BaseField):
    name = 'color'
    label = '颜色选择器'
    widget = 'color_input'
    properties = ['color_code', 'opacity']
    
    def render(self, value, mode='edit'):
        color_code = value.get('color_code', '#000000')
        opacity = value.get('opacity', 1)
        
        if mode == 'view':
            return f'<span style="display:inline-block;width:20px;height:20px;background:{color_code};opacity:{opacity};border:1px solid #ccc;"></span> {color_code}'
        
        return f'''
        <div class="color-input">
            <input type="color" name="{self.field_name}" value="{color_code}" class="form-control" style="width:60px;height:35px;">
            <input type="number" name="{self.field_name}_opacity" placeholder="透明度" value="{opacity}" min="0" max="1" step="0.1" class="form-control" style="width:80px;">
        </div>
        '''
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('color_code'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
