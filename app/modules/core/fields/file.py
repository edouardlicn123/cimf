from .base import BaseField

class FileField(BaseField):
    name = 'file'
    label = '文件'
    widget = 'file_input'
    properties = ['target_id', 'display', 'description']
    
    def render(self, value, mode='edit'):
        target_id = value.get('target_id', '')
        filename = value.get('filename', '')
        
        if mode == 'view':
            if target_id:
                return f'<a href="/files/{target_id}">{filename or "下载文件"}</a>'
            return ''
        
        return f'''
        <div class="file-input">
            <input type="file" name="{self.field_name}" class="form-control">
            <input type="hidden" name="{self.field_name}_id" value="{target_id}">
            {"<p>当前文件: " + filename + "</p>" if filename else ""}
        </div>
        '''
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('target_id'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
