# -*- coding: utf-8 -*-
"""
================================================================================
文件：telephone.py
路径：/home/edo/cimf-v2/core/fields/telephone.py
================================================================================

功能说明：
    电话号码字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class TelephoneField(BaseField):
    name = 'telephone'
    label = '电话'
    widget = 'input'
    properties = ['value', 'format']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            phone = value.get('value', '')
            return f'<a href="tel:{phone}">{phone}</a>' if phone else ''
        
        required = self.field_config.get('required', False)
        placeholder = self.field_config.get('placeholder', '请输入电话号码')
        
        return f'<input type="tel" name="{self.field_name}" value="{value.get("value", "")}" ' \
               f'class="form-control" placeholder="{placeholder}" {"required" if required else ""}>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
