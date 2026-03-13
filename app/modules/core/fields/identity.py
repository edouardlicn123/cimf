from .base import BaseField

class IdentityField(BaseField):
    name = 'identity'
    label = '证件识别码'
    widget = 'identity_input'
    properties = ['id_number', 'id_type', 'is_verified']
    
    def __init__(self, field_name, field_config):
        super().__init__(field_name, field_config)
        self.id_type = field_config.get('id_type', 'id_card')
    
    def render(self, value, mode='edit'):
        id_number = value.get('id_number', '')
        id_type = value.get('id_type', self.id_type)
        is_verified = value.get('is_verified', False)
        
        id_type_options = [
            {'value': 'id_card', 'label': '身份证'},
            {'value': 'passport', 'label': '护照'},
            {'value': 'driver_license', 'label': '驾驶证'},
            {'value': 'social_security', 'label': '社保卡'},
        ]
        
        options_html = ''.join([f'<option value="{opt["value"]}" {"selected" if opt["value"] == id_type else ""}>{opt["label"]}</option>' for opt in id_type_options])
        
        if mode == 'view':
            verified_badge = '<span class="badge bg-success">已验证</span>' if is_verified else '<span class="badge bg-secondary">未验证</span>'
            masked = id_number[:3] + '****' + id_number[-4:] if len(id_number) > 7 else '****'
            return f'{masked} {verified_badge}'
        
        return f'''
        <div class="identity-input">
            <select name="{self.field_name}_type" class="form-control mb-2">
                {options_html}
            </select>
            <input type="text" name="{self.field_name}" placeholder="证件号码" value="{id_number}" class="form-control">
        </div>
        '''
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('id_number'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
