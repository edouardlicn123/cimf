# -*- coding: utf-8 -*-
"""
模型注册表

将 node_type_slug 映射到对应的 Django 模型类
"""

from typing import Dict, Type, Optional


class ModelRegistry:
    """模型注册表"""
    
    _registry: Dict[str, Type] = {}
    
    @classmethod
    def register(cls, slug: str, model_class: Type):
        """注册模型"""
        cls._registry[slug] = model_class
    
    @classmethod
    def get_model(cls, slug: str):
        """动态获取模型类"""
        if slug in cls._registry and cls._registry[slug] is not None:
            return cls._registry[slug]
        
        # 动态导入模块模型
        try:
            from importlib import import_module
            mod = import_module(f'modules.{slug}.models')
            
            # 查找 Fields 结尾的模型类
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if (attr_name.endswith('Fields') and 
                    hasattr(attr, '_meta') and 
                    hasattr(attr, 'node')):
                    cls._registry[slug] = attr
                    return attr
        except (ImportError, ModuleNotFoundError):
            pass
        
        return None
    
    @classmethod
    def get_all_slugs(cls):
        """获取所有已注册的 slug"""
        return list(cls._registry.keys())
