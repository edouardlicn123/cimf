from .base import BaseField

class TextWithSummaryField(BaseField):
    name = 'text_with_summary'
    label = '含摘要文本'
    widget = 'text_with_summary'
    properties = ['value', 'summary', 'format']
    
    def render(self, value, mode='edit'):
        if mode == 'view':
            return value.get('value', '')
        return f'''
        <div class="text-with-summary">
            <textarea name="{self.field_name}" class="form-control" rows="6">{value.get("value", "")}</textarea>
            <label>摘要</label>
            <textarea name="{self.field_name}_summary" class="form-control" rows="2">{value.get("summary", "")}</textarea>
        </div>
        '''
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
