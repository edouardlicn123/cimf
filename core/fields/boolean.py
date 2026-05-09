# -*- coding: utf-8 -*-
"""
================================================================================
文件：boolean.py
路径：/home/edo/cimf-v2/core/fields/boolean.py
================================================================================

功能说明：
    布尔值字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class BooleanField(BaseField):
    name = 'boolean'
    label = '布尔值'
    widget = 'checkbox'
    properties = ['value']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        checked = 'checked' if value.get('value') else ''
        if mode == 'view':
            return '是' if value.get('value') else '否'
        
        return f'<div class="form-check form-switch">' \
               f'<input type="checkbox" name="{self.field_name}" class="form-check-input" role="switch" id="{self.field_name}" {checked}>' \
               f'<label class="form-check-label" for="{self.field_name}">{self.field_config.get("label", "")}</label></div>'
    
    def validate(self, value: dict) -> list:
        return []
