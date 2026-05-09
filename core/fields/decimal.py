# -*- coding: utf-8 -*-
"""
================================================================================
文件：decimal.py
路径：/home/edo/cimf-v2/core/fields/decimal.py
================================================================================

功能说明：
    小数字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class DecimalField(BaseField):
    name = 'decimal'
    label = '小数'
    widget = 'input'
    properties = ['value', 'min', 'max', 'decimal_places']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            return str(value.get('value', ''))
        
        min_val = self.field_config.get('min', '')
        max_val = self.field_config.get('max', '')
        required = self.field_config.get('required', False)
        placeholder = self.field_config.get('placeholder', '')
        
        attrs = f'step="0.01" min="{min_val}" ' if min_val else 'step="0.01" '
        attrs += f'max="{max_val}" ' if max_val else ''
        attrs += f'placeholder="{placeholder}"'
        
        return f'<input type="number" name="{self.field_name}" value="{value.get("value", "")}" ' \
               f'class="form-control" {attrs} {"required" if required else ""}>'
    
    def validate(self, value: dict) -> list:
        errors = []
        val = value.get('value')
        if self.field_config.get('required') and not val:
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
