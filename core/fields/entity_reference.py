# -*- coding: utf-8 -*-
"""
================================================================================
文件：entity_reference.py
路径：/home/edo/cimf-v2/core/fields/entity_reference.py
================================================================================

功能说明：
    实体引用字段类型（关联其他节点或词汇表）
    
版本：
    - 1.0: 从 Flask 迁移
"""

from .base import BaseField


class EntityReferenceField(BaseField):
    name = 'entity_reference'
    label = '实体引用'
    widget = 'select'
    properties = ['value', 'reference_type', 'reference_slug']
    
    def render(self, value: dict, mode: str = 'edit') -> str:
        if mode == 'view':
            return value.get('display', str(value.get('value', '')))
        
        ref_type = self.field_config.get('reference_type', 'taxonomy')
        ref_slug = self.field_config.get('reference_slug', '')
        required = self.field_config.get('required', False)
        
        options = self.field_config.get('options', [])
        options_html = ''.join([
            f'<option value="{opt["value"]}" {"selected" if str(opt["value"]) == str(value.get("value")) else ""}>{opt["label"]}</option>'
            for opt in options
        ])
        
        return f'<select name="{self.field_name}" class="form-select" {"required" if required else ""} ' \
               f'data-reference-type="{ref_type}" data-reference-slug="{ref_slug}">' \
               f'<option value="">请选择</option>{options_html}</select>'
    
    def validate(self, value: dict) -> list:
        errors = []
        if self.field_config.get('required') and not value.get('value'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
