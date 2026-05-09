# -*- coding: utf-8 -*-
"""
================================================================================
文件：masked.py
路径：/home/edo/cimf-v2/core/fields/masked.py
================================================================================

功能说明：
    脱敏字段类型（隐藏部分字符）
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class MaskedField(BaseField):
    name = 'masked'
    label = '脱敏文本'
    widget = 'input'
    properties = ['value', 'mask_type']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            val = value.get('value', '')
            mask_type = value.get('mask_type', self.field_config.get('mask_type', 'phone'))
            if mask_type == 'phone' and len(val) >= 7:
                return val[:3] + '****' + val[-4:]
            elif mask_type == 'email' and '@' in val:
                parts = val.split('@')
                return parts[0][:2] + '***@' + parts[1]
            return val
        
        required = self.field_config.get('required', False)
        placeholder = self.field_config.get('placeholder', '')
        
        return f'<input type="text" name="{self.field_name}" value="{value.get("value", "")}" ' \
               f'class="form-control" placeholder="{placeholder}" {"required" if required else ""}>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
