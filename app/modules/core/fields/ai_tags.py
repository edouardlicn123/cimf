from .base import BaseField

class AITagsField(BaseField):
    name = 'ai_tags'
    label = '智能标签'
    widget = 'ai_tags_input'
    properties = ['term_id', 'confidence_score']
    
    def render(self, value, mode='edit'):
        term_id = value.get('term_id', '')
        term_name = value.get('term_name', '')
        confidence = value.get('confidence_score', '')
        
        if mode == 'view':
            if term_name:
                return f'{term_name} <span class="text-muted">({confidence}%)</span>'
            return ''
        
        return f'''
        <div class="ai-tags-input">
            <input type="text" name="{self.field_name}" placeholder="输入文本自动生成标签" value="{term_name}" class="form-control mb-2">
            <input type="hidden" name="{self.field_name}_term_id" value="{term_id}">
            <input type="number" name="{self.field_name}_confidence" placeholder="置信度" value="{confidence}" class="form-control" min="0" max="100">
        </div>
        '''
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('term_id'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
