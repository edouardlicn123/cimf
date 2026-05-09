# -*- coding: utf-8 -*-
"""
================================================================================
文件：gis.py
路径：/home/edo/cimf-v2/core/fields/gis.py
================================================================================

功能说明：
    GIS 地理信息系统字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class GISField(BaseField):
    name = 'gis'
    label = 'GIS 地理信息'
    widget = 'input'
    properties = ['value', 'type', 'coordinates']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            coords = value.get('coordinates', value.get('value', {}).get('coordinates', []))
            if coords:
                return f'经度: {coords[0]}, 纬度: {coords[1]}'
            return ''
        
        required = self.field_config.get('required', False)
        coords = value.get('coordinates', value.get('value', {}).get('coordinates', []))
        lng = coords[0] if len(coords) > 0 else ''
        lat = coords[1] if len(coords) > 1 else ''
        
        return f'<div class="row g-2"><div class="col-6">' \
               f'<label class="form-label">经度</label>' \
               f'<input type="text" name="{self.field_name}_lng" value="{lng}" class="form-control"></div>' \
               f'<div class="col-6"><label class="form-label">纬度</label>' \
               f'<input type="text" name="{self.field_name}_lat" value="{lat}" class="form-control" {"required" if required else ""}></div></div>' \
               f'<small class="text-muted">输入坐标后可在地图上查看位置</small>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required'):
            coords = value.get('coordinates', value.get('value', {}).get('coordinates', []))
            if not coords or len(coords) < 2:
                errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
