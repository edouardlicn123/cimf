# -*- coding: utf-8 -*-
"""
================================================================================
文件：email.py
路径：/home/edo/cimf-v2/core/fields/email.py
================================================================================

功能说明：
    邮箱字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class EmailField(BaseField):
    name = 'email'
    label = '邮箱'
    widget = 'input'
    properties = ['value']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            email = value.get('value', '')
            return f'<a href="mailto:{email}">{email}</a>' if email else ''
        
        required = self.field_config.get('required', False)
        placeholder = self.field_config.get('placeholder', 'example@domain.com')
        
        return f'<input type="email" name="{self.field_name}" value="{value.get("value", "")}" ' \
               f'class="form-control" placeholder="{placeholder}" {"required" if required else ""}>'
    
    def validate(self, value: dict) -> list:
        errors = []
        email = value.get('value', '')
        if self.field_config.get('required') and not email:
            errors.append(f'{self.field_config.get("label")} 为必填项')
        if email and '@' not in email:
            errors.append(f'{self.field_config.get("label")} 格式不正确')
        return errors
