# -*- coding: utf-8 -*-
"""
================================================================================
文件：identity.py
路径：/home/edo/cimf-v2/core/fields/identity.py
================================================================================

功能说明：
    身份证号字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class IdentityField(BaseField):
    name = 'identity'
    label = '身份证号'
    widget = 'input'
    properties = ['value']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            id_num = value.get('value', '')
            if id_num and len(id_num) >= 8:
                return id_num[:4] + '****' + id_num[-4:]
            return id_num
        
        required = self.field_config.get('required', False)
        placeholder = self.field_config.get('placeholder', '请输入身份证号')
        
        return f'<input type="text" name="{self.field_name}" value="{value.get("value", "")}" ' \
               f'class="form-control" placeholder="{placeholder}" {"required" if required else ""}>'
    
    def validate(self, value: dict) -> list:
        errors = []
        id_num = value.get('value', '')
        if self.field_config.get('required') and not id_num:
            errors.append(f'{self.field_config.get("label")} 为必填项')
        if id_num and len(id_num) not in [15, 18]:
            errors.append(f'{self.field_config.get("label")} 身份证号格式不正确')
        return errors
