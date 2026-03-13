from .base import BaseField

class ImageField(BaseField):
    name = 'image'
    label = '图片'
    widget = 'image_input'
    properties = ['target_id', 'alt', 'title', 'width', 'height']
    
    def render(self, value, mode='edit'):
        target_id = value.get('target_id', '')
        alt = value.get('alt', '')
        
        if mode == 'view':
            if target_id:
                return f'<img src="/images/{target_id}" alt="{alt}" style="max-width:200px;">'
            return ''
        
        return f'''
        <div class="image-input">
            <input type="file" name="{self.field_name}" accept="image/*" class="form-control">
            <input type="hidden" name="{self.field_name}_id" value="{target_id}">
            <input type="text" name="{self.field_name}_alt" placeholder="图片描述" value="{alt}" class="form-control mt-2">
        </div>
        '''
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('target_id'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
