# -*- coding: utf-8 -*-
"""
===============================================================================
文件：integer.py
路径：/home/edo/cimf-v2/core/fields/integer.py
===============================================================================

功能说明：
    整数字段类型
    
版本：
    - 1.0: 从 Flask 迁移
    - 2.0: 使用简化模式调用基类方法
"""

from .base import BaseField


class IntegerField(BaseField):
    name = 'integer'
    label = '整数'
    widget = 'input'
    properties = ['value', 'min', 'max']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            return str(value.get('value', ''))
        
        min_val = self.field_config.get('min', '')
        max_val = self.field_config.get('max', '')
        
        extra_attrs = {}
        if min_val:
            extra_attrs['min'] = min_val
        if max_val:
            extra_attrs['max'] = max_val
        
        return self._render_input(input_type='number', **extra_attrs)
    
    def validate(self, value: dict) -> list:
        errors = self._validate_required()
        val = value.get('value')
        
        if val:
            try:
                int_val = int(val)
                errors.extend(self._validate_range(
                    min_value=int(self.field_config.get('min', float('-inf'))) if self.field_config.get('min') else None,
                    max_value=int(self.field_config.get('max', float('inf'))) if self.field_config.get('max') else None
                ))
            except ValueError:
                errors.append(f'{self.field_config.get("label")} 必须是整数')
        
        return errors
