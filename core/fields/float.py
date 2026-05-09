# -*- coding: utf-8 -*-
"""
================================================================================
文件：float.py
路径：/home/edo/cimf-v2/core/fields/float.py
================================================================================

功能说明：
    浮点数字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class FloatField(BaseField):
    name = 'float'
    label = '浮点数'
    widget = 'input'
    properties = ['value', 'min', 'max']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            return str(value.get('value', ''))
        
        required = self.field_config.get('required', False)
        placeholder = self.field_config.get('placeholder', '')
        
        return f'<input type="number" step="any" name="{self.field_name}" value="{value.get("value", "")}" ' \
               f'class="form-control" placeholder="{placeholder}" {"required" if required else ""}>'
    
    def validate(self, value: dict) -> list:
        errors = []
        val = value.get('value')
        if self.field_config.get('required') and not val:
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
