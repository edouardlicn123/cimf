# -*- coding: utf-8 -*-
"""
服务基类，提供通用 CRUD 方法
"""

from typing import Optional, Any


class BaseService:
    """
    服务基类
    
    子类必须定义 model_class 属性：
    class UserService(BaseService):
        model_class = User
    """
    model_class = None
    
    @classmethod
    def get_by_id(cls, entity_id: int) -> Optional[Any]:
        """根据 ID 获取对象"""
        if cls.model_class is None:
            raise NotImplementedError('子类必须定义 model_class')
        return cls.model_class.objects.filter(id=entity_id).first()
    
    @classmethod
    def get_by_slug(cls, slug: str) -> Optional[Any]:
        """根据 slug 获取对象（仅适用于有 slug 字段的模型）"""
        if cls.model_class is None:
            raise NotImplementedError('子类必须定义 model_class')
        return cls.model_class.objects.filter(slug=slug).first()
    
    @classmethod
    def get_list(cls, **filters) -> Any:
        """根据条件获取列表"""
        if cls.model_class is None:
            raise NotImplementedError('子类必须定义 model_class')
        return cls.model_class.objects.filter(**filters)
