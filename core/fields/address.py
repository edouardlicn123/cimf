# -*- coding: utf-8 -*-
"""
================================================================================
文件：address.py
路径：/home/edo/cimf-v2/core/fields/address.py
================================================================================

功能说明：
    地址字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class AddressField(BaseField):
    name = 'address'
    label = '地址'
    widget = 'textarea'
    properties = ['value', 'province', 'city', 'district', 'detail']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            parts = []
            if value.get('province'): parts.append(value.get('province'))
            if value.get('city'): parts.append(value.get('city'))
            if value.get('district'): parts.append(value.get('district'))
            if value.get('detail'): parts.append(value.get('detail'))
            return ''.join(parts)
        
        required = self.field_config.get('required', False)
        
        return f'<div class="row g-2 mb-2"><div class="col-4">' \
               f'<input type="text" name="{self.field_name}_province" value="{value.get("province", "")}" class="form-control" placeholder="省份"></div>' \
               f'<div class="col-4"><input type="text" name="{self.field_name}_city" value="{value.get("city", "")}" class="form-control" placeholder="城市"></div>' \
               f'<div class="col-4"><input type="text" name="{self.field_name}_district" value="{value.get("district", "")}" class="form-control" placeholder="区县"></div></div>' \
               f'<textarea name="{self.field_name}" class="form-control" rows="2" placeholder="详细地址" {"required" if required else ""}>{value.get("detail", value.get("value", ""))}</textarea>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value') and not value.get('detail'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
