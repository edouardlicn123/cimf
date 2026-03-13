from .base import BaseField

class EntityReferenceField(BaseField):
    name = 'entity_reference'
    label = '关联引用'
    widget = 'select'
    properties = ['target_id', 'target_type']
    
    def __init__(self, field_name, field_config):
        super().__init__(field_name, field_config)
        self.reference_type = field_config.get('reference_type', 'node')
    
    def render(self, value, mode='edit'):
        target_id = value.get('target_id', '')
        target_type = value.get('target_type', self.reference_type)
        
        options = self.field_config.get('options', [])
        options_html = ''.join([f'<option value="{opt["id"]}" {"selected" if opt["id"] == target_id else ""}>{opt["label"]}</option>' for opt in options])
        
        if mode == 'view':
            for opt in options:
                if str(opt['id']) == str(target_id):
                    return opt.get('label', '')
            return ''
        
        return f'<select name="{self.field_name}" class="form-control"><option value="">请选择</option>{options_html}</select>'
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('target_id'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
