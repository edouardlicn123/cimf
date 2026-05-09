# -*- coding: utf-8 -*-
"""
字段提取器

从 Django 模型中提取字段信息用于导入导出
支持自动发现和模块补充指定
"""

from typing import List, Dict, Type, Optional, Any
from django.db import models


class FieldDefExtractor:
    """字段定义提取器"""
    
    EXCLUDE_FIELDS = {'id', 'node', 'created_at', 'updated_at'}
    
    FIELD_TYPE_MAP = {
        'AutoField': 'auto',
        'BigAutoField': 'auto',
        'CharField': 'string',
        'TextField': 'text',
        'IntegerField': 'integer',
        'BigIntegerField': 'integer',
        'FloatField': 'float',
        'DecimalField': 'decimal',
        'BooleanField': 'boolean',
        'DateField': 'date',
        'DateTimeField': 'datetime',
        'EmailField': 'email',
        'URLField': 'url',
        'JSONField': 'json',
        'ForeignKey': 'fk',
    }
    
    FK_TAXONOMY_MAP = {
        'customer_type': 'customer_type',
        'customer_level': 'customer_level',
        'country': 'country',
        'enterprise_type': 'enterprise_type',
        'industry': 'industry',
        'enterprise_nature': 'enterprise_nature',
        'resident_type': 'resident_type',
        'grid': 'grid',
        'key_category': 'key_category',
        'nation': 'nation',
        'political_status': 'political_status',
        'marital_status': 'marital_status',
        'education': 'education_level',
        'health_status': 'health_status',
        'gender': 'gender',
        'relation': 'resident_relation',
        'other_id_type': 'other_id_type',
    }
    
    @classmethod
    def extract(cls, model_class: Type) -> List[Dict]:
        """从 Django 模型提取字段定义"""
        fields = []
        
        for field in model_class._meta.get_fields():
            if not hasattr(field, 'attname'):
                continue
            if field.name in cls.EXCLUDE_FIELDS:
                continue
            
            field_type = cls._get_field_type(field)
            if field_type == 'unknown':
                continue
            
            field_info = {
                'name': field.name,
                'label': cls._get_verbose_name(field),
                'type': field_type,
                'required': cls._is_required(field),
            }
            
            if isinstance(field, models.ForeignKey):
                field_info['fk_to'] = field.related_model._meta.model_name
                field_info['taxonomy'] = cls.FK_TAXONOMY_MAP.get(field.name)
            
            if hasattr(field, 'choices') and field.choices:
                field_info['choices'] = [{'value': c[0], 'label': c[1]} for c in field.choices]
            
            if hasattr(field, 'max_length'):
                field_info['max_length'] = field.max_length
            
            fields.append(field_info)
        
        return fields
    
    @classmethod
    def _get_field_type(cls, field) -> str:
        """获取字段类型映射"""
        field_class_name = field.__class__.__name__
        return cls.FIELD_TYPE_MAP.get(field_class_name, 'unknown')
    
    @classmethod
    def _get_verbose_name(cls, field) -> str:
        """获取字段显示名称"""
        verbose_name = getattr(field, 'verbose_name', None)
        if verbose_name:
            if hasattr(verbose_name, '__str__'):
                verbose_name = str(verbose_name)
            return verbose_name
        return field.name
    
    @classmethod
    def _is_required(cls, field) -> bool:
        """判断字段是否必填"""
        if hasattr(field, 'blank') and hasattr(field, 'null'):
            if not field.blank and not field.null and not field.has_default():
                return True
        return False
    
    @classmethod
    def merge_with_module_config(cls, auto_fields: List[Dict], 
                                  module_config: Optional[List[Dict]]) -> List[Dict]:
        """
        合并自动发现的字段和模块配置
        
        处理优先级：
        1. exclude: True → 从结果中移除
        2. 覆盖 → 用模块配置覆盖
        3. 补充 → 追加新字段
        """
        if not module_config:
            return auto_fields
        
        result = {f['name']: f for f in auto_fields}
        
        for config in module_config:
            name = config.get('name')
            if not name:
                continue
            
            if config.get('exclude'):
                result.pop(name, None)
            elif name in result:
                result[name].update(config)
                if 'exclude' in result[name]:
                    del result[name]['exclude']
            else:
                result[name] = dict(config)
                if 'exclude' in result[name]:
                    del result[name]['exclude']
        
        return list(result.values())
