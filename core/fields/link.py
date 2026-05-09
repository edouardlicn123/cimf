# -*- coding: utf-8 -*-
"""
================================================================================
文件：link.py
路径：/home/edo/cimf-v2/core/fields/link.py
================================================================================

功能说明：
    链接字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class LinkField(BaseField):
    name = 'link'
    label = '链接'
    widget = 'input'
    properties = ['value', 'url', 'title']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            url = value.get('url', value.get('value', ''))
            title = value.get('title', url)
            return f'<a href="{url}" target="_blank">{title}</a>'
        
        required = self.field_config.get('required', False)
        
        return f'<div class="input-group mb-2"><span class="input-group-text">链接文字</span>' \
               f'<input type="text" name="{self.field_name}_title" value="{value.get("title", "")}" class="form-control"></div>' \
               f'<div class="input-group"><span class="input-group-text">URL</span>' \
               f'<input type="url" name="{self.field_name}" value="{value.get("url", value.get("value", ""))}" ' \
               f'class="form-control" {"required" if required else ""}></div>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value') and not value.get('url'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
