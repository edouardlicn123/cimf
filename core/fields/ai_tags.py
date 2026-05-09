# -*- coding: utf-8 -*-
"""
================================================================================
文件：ai_tags.py
路径：/home/edo/cimf-v2/core/fields/ai_tags.py
================================================================================

功能说明：
    AI 标签字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class AITagsField(BaseField):
    name = 'ai_tags'
    label = 'AI 标签'
    widget = 'input'
    properties = ['value', 'tags']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            tags = value.get('tags', value.get('value', []))
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(',')]
            return ', '.join([f'<span class="badge bg-info">{t}</span>' for t in tags]) if tags else ''
        
        required = self.field_config.get('required', False)
        tags_value = ','.join(value.get('tags', value.get('value', [])))
        
        return f'<input type="text" name="{self.field_name}" value="{tags_value}" ' \
               f'class="form-control" placeholder="标签1, 标签2, 标签3" {"required" if required else ""}>' \
               f'<small class="text-muted">多个标签用逗号分隔</small>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
