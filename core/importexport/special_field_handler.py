# -*- coding: utf-8 -*-
"""
特殊字段处理器

处理 JSON 字段、Region 字段等特殊类型的导入导出
"""

import json
from typing import Any, Dict, Optional


class SpecialFieldPool:
    """特殊字段处理器池"""
    
    _handlers = {}
    
    @classmethod
    def register(cls, field_name: str, handler):
        """注册处理器"""
        cls._handlers[field_name] = handler
    
    @classmethod
    def is_special_field(cls, field_name: str) -> bool:
        """检查是否为特殊字段"""
        return field_name in cls._handlers
    
    @classmethod
    def handle_export(cls, field_name: str, value: Any) -> str:
        """处理导出时的特殊字段值"""
        if field_name in cls._handlers:
            return cls._handlers[field_name].handle_export(value)
        return cls._default_export(field_name, value)
    
    @classmethod
    def handle_import(cls, field_name: str, value: str) -> Any:
        """处理导入时的特殊字段值"""
        if field_name in cls._handlers:
            return cls._handlers[field_name].handle_import(value)
        return cls._default_import(field_name, value)
    
    @staticmethod
    def _default_export(field_name: str, value: Any) -> str:
        """默认导出处理"""
        if value is None:
            return ''
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)
    
    @staticmethod
    def _default_import(field_name: str, value: str) -> Any:
        """默认导入处理"""
        if not value:
            return None
        
        if field_name == 'region':
            try:
                if isinstance(value, str):
                    return json.loads(value)
                return value
            except json.JSONDecodeError:
                return None
        
        if field_name in ('registered_capital', 'credit_limit'):
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        return value


class RegionFieldHandler:
    """省市区字段处理器"""
    
    @classmethod
    def handle_export(cls, value: Any) -> str:
        """导出：JSON -> 字符串"""
        if not value:
            return ''
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)
    
    @classmethod
    def handle_import(cls, value: str) -> Optional[Dict]:
        """导入：字符串/JSON -> JSON"""
        if not value:
            return None
        
        if isinstance(value, dict):
            return value
        
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {'raw': value}


SpecialFieldPool.register('region', RegionFieldHandler())
