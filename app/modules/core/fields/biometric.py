from .base import BaseField

class BiometricField(BaseField):
    name = 'biometric'
    label = '生物特征引用'
    widget = 'biometric_input'
    properties = ['feature_vector', 'type', 'version']
    
    def render(self, value, mode='edit'):
        b_type = value.get('type', 'fingerprint')
        version = value.get('version', '1.0')
        
        type_options = [
            {'value': 'fingerprint', 'label': '指纹'},
            {'value': 'face', 'label': '人脸'},
            {'value': 'iris', 'label': '虹膜'},
            {'value': 'voice', 'label': '声纹'},
        ]
        
        options_html = ''.join([f'<option value="{opt["value"]}" {"selected" if opt["value"] == b_type else ""}>{opt["label"]}</option>' for opt in type_options])
        
        if mode == 'view':
            type_label = next((opt['label'] for opt in type_options if opt['value'] == b_type), b_type)
            return f'{type_label} (v{version})'
        
        return f'''
        <div class="biometric-input">
            <select name="{self.field_name}_type" class="form-control mb-2">
                {options_html}
            </select>
            <input type="text" name="{self.field_name}_version" placeholder="版本号" value="{version}" class="form-control">
        </div>
        '''
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('type'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
