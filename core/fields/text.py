# -*- coding: utf-8 -*-
"""
===============================================================================
文件：text.py
路径：/home/edo/cimf-v2/core/fields/text.py
===============================================================================

功能说明：
    带格式文本字段类型
    
版本：
    - 1.0: 从 Flask 迁移
    - 2.0: 使用简化模式调用基类方法
"""

from .base import BaseField


class TextField(BaseField):
    name = 'text'
    label = '带格式文本'
    widget = 'rich_text'
    properties = ['value', 'format']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            return value.get('value', '')
        return self._render_textarea(rows=5)
    
    def validate(self, value: dict) -> list:
        return self._validate_required()
