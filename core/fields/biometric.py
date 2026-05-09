# -*- coding: utf-8 -*-
"""
================================================================================
文件：biometric.py
路径：/home/edo/cimf-v2/core/fields/biometric.py
================================================================================

功能说明：
    生物识别字段类型
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class BiometricField(BaseField):
    name = 'biometric'
    label = '生物识别'
    widget = 'input'
    properties = ['value', 'biometric_type']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            return '已录入' if value.get('value') else '未录入'
        
        required = self.field_config.get('required', False)
        bio_type = self.field_config.get('biometric_type', 'fingerprint')
        
        return f'<input type="hidden" name="{self.field_name}" value="{value.get("value", "")}">' \
               f'<div class="alert alert-info mb-0">' \
               f'<i class="bi bi-fingerprint"></i> 生物识别类型: {bio_type}<br>' \
               f'<small>生物特征数据将加密存储</small></div>'
    
    def validate(self, value: dict) -> list:
        return []
