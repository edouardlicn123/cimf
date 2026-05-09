# -*- coding: utf-8 -*-
"""
================================================================================
文件：text_long.py
路径：/home/edo/cimf-v2/core/fields/text_long.py
================================================================================

功能说明：
    长文本字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class TextLongField(BaseField):
    name = 'text_long'
    label = '长文本'
    widget = 'textarea'
    properties = ['value', 'rows']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            return value.get('value', '').replace('\n', '<br>')
        
        rows = self.field_config.get('rows', 5)
        required = self.field_config.get('required', False)
        placeholder = self.field_config.get('placeholder', '')
        
        return f'<textarea name="{self.field_name}" rows="{rows}" class="form-control" ' \
               f'{"required" if required else ""} placeholder="{placeholder}">{value.get("value", "")}</textarea>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
