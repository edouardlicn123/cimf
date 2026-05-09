# -*- coding: utf-8 -*-
"""
================================================================================
文件：image.py
路径：/home/edo/cimf-v2/core/fields/image.py
================================================================================

功能说明：
    图片上传字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class ImageField(BaseField):
    name = 'image'
    label = '图片'
    widget = 'file_input'
    properties = ['value', 'max_width', 'max_height']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            if value.get('value'):
                return f'<img src="{value.get("url", "")}" alt="{value.get("filename", "")}" style="max-width: 200px;">'
            return ''
        
        required = self.field_config.get('required', False)
        
        current_image = f'<div class="mb-2"><img src="{value.get("url", "")}" alt="当前图片" style="max-width: 200px;"></div>' if value.get('value') else ''
        
        return f'{current_image}<input type="file" name="{self.field_name}" class="form-control" ' \
               f'accept="image/*" {"required" if required else ""}>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
