# -*- coding: utf-8 -*-
"""
================================================================================
文件：timestamp.py
路径：/home/edo/cimf-v2/core/fields/timestamp.py
================================================================================

功能说明：
    时间戳字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class TimestampField(BaseField):
    name = 'timestamp'
    label = '时间戳'
    widget = 'input'
    properties = ['value', 'auto_now']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            return value.get('value', '')
        
        required = self.field_config.get('required', False)
        
        return f'<input type="text" name="{self.field_name}" value="{value.get("value", "")}" ' \
               f'class="form-control" placeholder="Unix 时间戳" {"required" if required else ""}>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
