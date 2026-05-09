# -*- coding: utf-8 -*-
"""
===============================================================================
文件：string.py
路径：/home/edo/cimf-v2/core/fields/string.py
===============================================================================

功能说明：
    单行文本字段类型
    
版本：
    - 1.0: 从 Flask 迁移
    - 2.0: 使用简化模式调用基类方法
"""

from .base import BaseField


class StringField(BaseField):
    name = 'string'
    label = '单行文本'
    widget = 'input'
    properties = ['value', 'max_length']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            return value.get('value', '')
        return self._render_input(
            input_type='text',
            max_length=self.field_config.get('max_length', 255),
            placeholder=self.field_config.get('placeholder', '')
        )
    
    def validate(self, value: dict) -> list:
        return self._validate_required()
