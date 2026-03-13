from .base import BaseField

class MaskedField(BaseField):
    name = 'masked'
    label = '隐私脱敏字段'
    widget = 'masked_input'
    properties = ['raw_value', 'display_value', 'permission_level']
    
    def __init__(self, field_name, field_config):
        super().__init__(field_name, field_config)
        self.masking_type = field_config.get('masking_type', 'partial')
    
    def render(self, value, mode='edit'):
        raw_value = value.get('raw_value', '')
        display_value = value.get('display_value', '')
        permission_level = value.get('permission_level', 'public')
        
        if mode == 'view':
            return display_value or '******'
        
        return f'''
        <div class="masked-input">
            <input type="password" name="{self.field_name}" placeholder="输入原始值" value="{raw_value}" class="form-control mb-2">
            <select name="{self.field_name}_permission" class="form-control">
                <option value="public" {"selected" if permission_level == "public" else ""}>公开</option>
                <option value="restricted" {"selected" if permission_level == "restricted" else ""}>受限</option>
                <option value="confidential" {"selected" if permission_level == "confidential" else ""}>机密</option>
            </select>
        </div>
        '''
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('raw_value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
