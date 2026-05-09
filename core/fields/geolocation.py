# -*- coding: utf-8 -*-
"""
================================================================================
文件：geolocation.py
路径：/home/edo/cimf-v2/core/fields/geolocation.py
================================================================================

功能说明：
    地理位置字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class GeolocationField(BaseField):
    name = 'geolocation'
    label = '地理位置'
    widget = 'input'
    properties = ['value', 'latitude', 'longitude']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            lat = value.get('latitude', '')
            lng = value.get('longitude', '')
            return f'纬度: {lat}, 经度: {lng}' if lat and lng else ''
        
        required = self.field_config.get('required', False)
        lat = value.get('latitude', value.get('value', {}).get('latitude', ''))
        lng = value.get('longitude', value.get('value', {}).get('longitude', ''))
        
        return f'<div class="row g-2"><div class="col-6">' \
               f'<label class="form-label">纬度</label>' \
               f'<input type="text" name="{self.field_name}_lat" value="{lat}" class="form-control"></div>' \
               f'<div class="col-6"><label class="form-label">经度</label>' \
               f'<input type="text" name="{self.field_name}_lng" value="{lng}" class="form-control" {"required" if required else ""}></div></div>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
