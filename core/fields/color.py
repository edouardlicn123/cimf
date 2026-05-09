# -*- coding: utf-8 -*-
"""
================================================================================
文件：color.py
路径：/home/edo/cimf-v2/core/fields/color.py
================================================================================

功能说明：
    颜色选择字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class ColorField(BaseField):
    name = 'color'
    label = '颜色'
    widget = 'color_input'
    properties = ['value']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            color = value.get('value', '')
            return f'<span style="display: inline-block; width: 20px; height: 20px; background-color: {color}; border: 1px solid #ccc;"></span> {color}'
        
        required = self.field_config.get('required', False)
        
        return f'<div class="input-group"><input type="color" name="{self.field_name}" value="{value.get("value", "#000000")}" ' \
               f'class="form-control form-control-color" {"required" if required else ""}></div>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
