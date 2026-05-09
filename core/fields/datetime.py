# -*- coding: utf-8 -*-
"""
================================================================================
文件：datetime.py
路径：/home/edo/cimf-v2/core/fields/datetime.py
================================================================================

功能说明：
    日期时间字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class DatetimeField(BaseField):
    name = 'datetime'
    label = '日期时间'
    widget = 'datetime_input'
    properties = ['value', 'min', 'max']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            return value.get('value', '')
        
        required = self.field_config.get('required', False)
        
        return f'<input type="datetime-local" name="{self.field_name}" value="{value.get("value", "")}" ' \
               f'class="form-control" {"required" if required else ""}>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
