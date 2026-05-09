# -*- coding: utf-8 -*-
"""
================================================================================
文件：text_with_summary.py
路径：/home/edo/cimf-v2/core/fields/text_with_summary.py
================================================================================

功能说明：
    带摘要文本字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class TextWithSummaryField(BaseField):
    name = 'text_with_summary'
    label = '带摘要文本'
    widget = 'rich_text'
    properties = ['value', 'summary', 'format']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            return f'<strong>摘要：</strong>{value.get("summary", "")}<br><strong>正文：</strong>{value.get("value", "")}'
        
        required = self.field_config.get('required', False)
        
        return f'<div class="text-with-summary">' \
               f'<div class="mb-2"><label>摘要</label>' \
               f'<input type="text" name="{self.field_name}_summary" value="{value.get("summary", "")}" class="form-control"></div>' \
               f'<div><label>正文</label>' \
               f'<textarea name="{self.field_name}" class="form-control" ' \
               f'{"required" if required else ""}>{value.get("value", "")}</textarea></div></div>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
