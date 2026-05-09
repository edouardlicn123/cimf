# -*- coding: utf-8 -*-
"""
================================================================================
文件：file.py
路径：/home/edo/cimf-v2/core/fields/file.py
================================================================================

功能说明：
    文件上传字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class FileField(BaseField):
    name = 'file'
    label = '文件'
    widget = 'file_input'
    properties = ['value', 'allowed_extensions', 'max_size']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            if value.get('value'):
                return f'<a href="{value.get("url", "#")}">{value.get("filename", "下载文件")}</a>'
            return ''
        
        required = self.field_config.get('required', False)
        accept = self.field_config.get('allowed_extensions', '')
        
        current_file = f'<div class="mb-2"><a href="{value.get("url", "#")}">{value.get("filename", "当前文件")}</a></div>' if value.get('value') else ''
        
        return f'{current_file}<input type="file" name="{self.field_name}" class="form-control" ' \
               f'accept="{accept}" {"required" if required else ""}>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
