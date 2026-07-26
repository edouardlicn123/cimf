"""
Node 模块基础服务类

为 node 类型模块提供可继承的标准 CRUD 方法。
继承自 BaseService，提供通用 CRUD 能力。
子类覆盖 model_class 后即可使用。

用法：
    class MyNodeService(BaseNodeService):
        model_class = MyFieldsModel
"""

from datetime import timedelta

from django.utils import timezone

from core.services.base_service import BaseService


class BaseNodeService(BaseService):
    model_class = None

    @classmethod
    def get_by_node_id(cls, node_id: int):
        if cls.model_class is None:
            return None
        return cls.model_class.objects.filter(node_id=node_id).first()

    @classmethod
    def get_count(cls):
        if cls.model_class is None:
            return 0
        return cls.model_class.objects.count()

    @classmethod
    def get_recent_count(cls, days: int = 7):
        if cls.model_class is None:
            return 0
        cutoff = timezone.now() - timedelta(days=days)
        return cls.model_class.objects.filter(created_at__gte=cutoff).count()
