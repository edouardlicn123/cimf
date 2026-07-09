"""
服务基类，提供通用 CRUD 方法
"""

from typing import Any


class BaseService:
    """
    服务基类

    子类必须定义 model_class 属性：
    class UserService(BaseService):
        model_class = User
    """

    model_class = None

    @classmethod
    def get_by_id(cls, entity_id: int) -> Any | None:
        """根据 ID 获取对象"""
        if cls.model_class is None:
            raise NotImplementedError("子类必须定义 model_class")
        return cls.model_class.objects.filter(id=entity_id).first()

    @classmethod
    def get_by_slug(cls, slug: str) -> Any | None:
        """根据 slug 获取对象（仅适用于有 slug 字段的模型）"""
        if cls.model_class is None:
            raise NotImplementedError("子类必须定义 model_class")
        return cls.model_class.objects.filter(slug=slug).first()

    @classmethod
    def get_list(cls, **filters) -> Any:
        """根据条件获取列表"""
        if cls.model_class is None:
            raise NotImplementedError("子类必须定义 model_class")
        return cls.model_class.objects.filter(**filters)

    @classmethod
    def create(cls, **kwargs) -> Any:
        """创建新对象"""
        if cls.model_class is None:
            raise NotImplementedError("子类必须定义 model_class")
        return cls.model_class.objects.create(**kwargs)

    @classmethod
    def update(cls, entity_id: int, **kwargs) -> tuple[Any, bool]:
        """更新对象，返回 (对象, 是否已变更)"""
        instance = cls.get_by_id(entity_id)
        if instance is None:
            return None, False
        changed = False
        for key, value in kwargs.items():
            if getattr(instance, key) != value:
                setattr(instance, key, value)
                changed = True
        if changed:
            instance.save()
        return instance, changed

    @classmethod
    def delete(cls, entity_id: int) -> bool:
        """删除对象"""
        instance = cls.get_by_id(entity_id)
        if instance is None:
            return False
        instance.delete()
        return True

    @classmethod
    def get_or_raise(cls, entity_id: int, error_msg: str | None = None) -> Any:
        """根据 ID 获取对象，不存在则抛出异常"""
        instance = cls.get_by_id(entity_id)
        if not instance:
            raise ValueError(error_msg or f"{cls.model_class.__name__} 不存在 (ID: {entity_id})")
        return instance

    @classmethod
    def get_first(cls, **filters) -> Any:
        """根据条件获取第一个对象"""
        if cls.model_class is None:
            raise NotImplementedError("子类必须定义 model_class")
        return cls.model_class.objects.filter(**filters).first()


